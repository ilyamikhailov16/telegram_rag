import logging
from abc import ABC, abstractmethod
from typing import Any
from openai import OpenAI, RateLimitError, BadRequestError, APIError
from config import config
from sqlalchemy import CursorResult, create_engine, text

from config import config
from prompts import sql_generator_prompt, responder_prompt


class LLMClient(ABC):
    @abstractmethod
    def get_answer(self, user_prompt: str, *args, **kwargs) -> Any:
        raise NotImplementedError

    def __call__(self, user_prompt: str, *args, **kwargs) -> Any:
        return self.get_answer(user_prompt, *args, **kwargs)


class OpenRouterClient(LLMClient):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model_path: str,
        system_prompt: str,
        max_retries: int,
    ) -> None:
        """Object initialization. The model and system prompt are fixed"""

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.model_path = model_path
        self.system_prompt = system_prompt
        self.max_retries = max_retries

    def get_answer(self, user_prompt: str) -> str | None:
        """Requesting LLM server and receiving a response."""

        retries_num = self.max_retries
        while retries_num > 0:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_path,
                    messages=[
                        {
                            "role": "system",
                            "content": self.system_prompt,
                        },
                        {
                            "role": "user",
                            "content": user_prompt,
                        },
                    ],
                    temperature=0,
                )
                return response.choices[0].message.content

            except (BadRequestError, APIError, RateLimitError) as e:
                logging.exception(f"API error (non-retryable): {e}")
                return None
            except Exception as e:
                logging.exception(
                    f"Transient error, retrying ({retries_num} left): {e}"
                )
                retries_num -= 1

        logging.error("Number of retries were exceeded.")
        return None


class SQLExecutor:
    def __init__(self, db_url: str) -> None:
        self.engine = create_engine(db_url)

    def execute_query(self, query: str) -> CursorResult[Any]:
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return result


class RAGService:
    def __init__(
        self, sql_generator: LLMClient, responder: LLMClient, sql_executor: SQLExecutor
    ) -> None:
        self.sql_generator = sql_generator
        self.responder = responder
        self.sql_executor = sql_executor

    def get_answer(self, question: str) -> str | None:
        sql_query = self.sql_generator(question)
        if not sql_query:
            logging.error("Failed to generate SQL query.")
            return None

        try:
            query_result = self.sql_executor.execute_query(sql_query)
            result_str = "\n".join([str(row) for row in query_result])
        except Exception as e:
            logging.exception(f"SQL execution error: {e}")
            return None

        answer = self.responder(
            f"Question: {question}\nSQL Query: {sql_query}\nResult: {result_str}"
        )
        return answer

    def __call__(self, question: str) -> str | None:
        return self.get_answer(question)


rag_service = RAGService(
    sql_generator=OpenRouterClient(
        base_url=config.base_url,
        api_key=config.api_token,
        model_path=config.model_path,
        system_prompt=sql_generator_prompt,
        max_retries=config.max_retries,
    ),
    responder=OpenRouterClient(
        base_url=config.base_url,
        api_key=config.api_token,
        model_path=config.model_path,
        system_prompt=responder_prompt,
        max_retries=config.max_retries,
    ),
    sql_executor=SQLExecutor(db_url=config.db_url),
)
