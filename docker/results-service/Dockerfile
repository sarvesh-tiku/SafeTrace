FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install pydantic rich pandas boto3 typer
COPY safetrace/ ./safetrace/
COPY scripts/ ./scripts/
ENV PYTHONPATH=/app
VOLUME ["/results"]
RUN useradd -m -u 1004 results
USER results
CMD ["python", "scripts/summarize_results.py", "--input", "/results/main_results.csv"]
