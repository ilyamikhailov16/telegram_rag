# Base image
FROM python:3.12-slim
# Working directory inside the container
WORKDIR /app
# Copy only the dependencies file first to leverage Docker layer caching
# so installing dependencies won't run again on every code change
COPY ./requirements.txt /app/requirements.txt
# Install dependencies
RUN pip3 install -r /app/requirements.txt
# Copy application code into the container
COPY ./data /app/data
COPY ./.env /app/.env
COPY ./bot.py /app/bot.py
COPY ./config.py /app/config.py
COPY ./database.py /app/database.py
COPY ./exceptions.py /app/exceptions.py
COPY ./main.py /app/main.py
COPY ./prompts.py /app/prompts.py
COPY ./rag.py /app/rag.py
# Port exposed by the container
EXPOSE 8005
# Command to run when the container starts
CMD ["/bin/sh", "-c", "python ./database.py && python ./main.py"]