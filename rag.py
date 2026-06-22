import logging
from abc import ABC, abstractmethod
from typing import Any
from openai import OpenAI, RateLimitError, BadRequestError, APIError
from config import config
from sqlalchemy import CursorResult, create_engine, text

from config import config
from prompts import sql_generator_prompt, responder_prompt
from exceptions import InvalidSQLQueryError


class LLMClient(ABC):
    @abstractmethod
    def get_answer(self, system_prompt: str, user_prompt: str, *args, **kwargs) -> Any:
        """Return an answer for the given user prompt.

        Subclasses must implement this method to call a language model
        (or compatible client) and return the model's response. The
        method should accept the prompt and any optional parameters
        required by the concrete implementation.
        """
        raise NotImplementedError

    def __call__(self, system_prompt: str, user_prompt: str, *args, **kwargs) -> Any:
        return self.get_answer(system_prompt, user_prompt, *args, **kwargs)


class OpenRouterClient(LLMClient):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model_path: str,
        max_retries: int,
    ) -> None:
        """Initialize an OpenAI-compatible client wrapper.

        Args:
            base_url: Base URL for the API endpoint.
            api_key: API key or token for authentication.
            model_path: Model identifier to use for completions.
            system_prompt: System prompt to include with each request.
            max_retries: Number of retries for transient errors.
        """

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.model_path = model_path
        self.max_retries = max_retries

    def get_answer(self, system_prompt: str, user_prompt: str) -> str:
        """Send the prompt to the wrapped client and return the response text."""
        retries_num = self.max_retries
        while retries_num > 0:
            try:
                # Limit tokens to avoid exceeding account credit/token budget
                response = (
                    self.client.chat.completions.create(
                        model=self.model_path,
                        messages=[
                            {
                                "role": "system",
                                "content": system_prompt,
                            },
                            {
                                "role": "user",
                                "content": user_prompt,
                            },
                        ],
                        temperature=config.temperature,
                        max_tokens=config.max_tokens,
                    )
                    .choices[0]
                    .message.content
                )

                if not response:
                    raise ValueError("Received empty response from OpenRouterClient.")
                return response

            except (BadRequestError, APIError, RateLimitError):
                raise

            except Exception as e:
                logging.exception(
                    f"Transient error in OpenRouterClient, retrying ({retries_num} left): {e}"
                )
                retries_num -= 1

        raise RuntimeError("Failed to get answer from OpenRouterClient after retries.")


class SQLExecutor:
    def __init__(self, db_url: str) -> None:
        """Create a SQL executor bound to `db_url`.

        The executor manages a SQLAlchemy engine used to run SQL
        statements against the configured database URL.
        """
        self.engine = create_engine(db_url)

    def execute_query(self, query: str) -> CursorResult[Any]:
        """Execute the provided SQL `query` and return the raw result.

        The caller is responsible for converting or formatting rows
        from the returned `CursorResult`.
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return result


class RAGService:
    def __init__(
        self,
        llm_client: LLMClient,
        sql_executor: SQLExecutor,
        max_retries: int,
        sql_generator_prompt: str,
        responder_prompt: str,
    ) -> None:
        self.llm_client = llm_client
        self.sql_executor = sql_executor
        self.max_retries = max_retries
        self.sql_generator_prompt = sql_generator_prompt
        self.responder_prompt = responder_prompt

    def get_answer(self, question: str) -> str:
        """Generate SQL from `question`, execute it, and produce a response.

        Workflow:
        1. Ask the `sql_generator` to produce a SQL query for `question`.
        2. Execute the SQL using `sql_executor` and collect results.
        3. Ask the `responder` to produce a human-readable answer using
           the question, SQL, and query results.

        Retries are attempted up to `self.max_retries` on any exception.
        Returns the responder's text on success, or `None` if retries
        are exhausted.
        """
        retries_num = self.max_retries
        while retries_num > 0:
            try:
                sql_query = self.llm_client(self.sql_generator_prompt, question)
                if not sql_query.strip().lower().startswith("select"):
                    raise InvalidSQLQueryError("Only 'SELECT' queries are allowed.")

                query_result = self.sql_executor.execute_query(sql_query)
                result_str = "\n".join([str(row) for row in query_result])

                answer = self.llm_client(
                    self.responder_prompt,
                    f"Question: {question}\nSQL Query: {sql_query}\nResult: {result_str}",
                )
                return answer

            except (BadRequestError, APIError, RateLimitError):
                raise

            except InvalidSQLQueryError:
                raise

            except Exception as e:
                logging.exception(
                    f"Transient error in RAG pipeline, retrying ({retries_num} left): {e}"
                )
                retries_num -= 1

        raise RuntimeError("Failed to get answer from RAGService after retries.")

    def __call__(self, question: str) -> str:
        """Call `get_answer` so the service can be used like a function.

        This forwards to `get_answer` and returns the same result.
        """
        return self.get_answer(question)


rag_service = RAGService(
    llm_client=OpenRouterClient(
        base_url=config.base_url,
        api_key=config.api_token,
        model_path=config.model_path,
        max_retries=config.client_max_retries,
    ),
    sql_executor=SQLExecutor(db_url=config.db_url),
    max_retries=config.rag_max_retries,
    sql_generator_prompt=sql_generator_prompt,
    responder_prompt=responder_prompt,
)
