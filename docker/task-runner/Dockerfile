FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml .
RUN pip install pytest gitpython pydantic
COPY safetrace/ ./safetrace/
ENV PYTHONPATH=/app
RUN useradd -m -u 1000 runner
USER runner
CMD ["python", "-m", "safetrace.test_runner"]
