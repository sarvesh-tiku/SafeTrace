FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e ".[dev]"
COPY safetrace/ ./safetrace/
COPY scripts/ ./scripts/
COPY benchmark/ ./benchmark/
ENV PYTHONPATH=/app
CMD ["python", "scripts/run_agent.py"]
