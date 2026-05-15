FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install pydantic rich prometheus-client
COPY safetrace/ ./safetrace/
ENV PYTHONPATH=/app
RUN useradd -m -u 1001 monitor
USER monitor
CMD ["python", "-c", "from safetrace.monitor import run_monitor; print('monitor-service ready')"]
