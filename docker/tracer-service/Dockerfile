FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install pydantic rich boto3
COPY safetrace/ ./safetrace/
ENV PYTHONPATH=/app
VOLUME ["/results"]
RUN useradd -m -u 1003 tracer
USER tracer
CMD ["python", "-c", "from safetrace.tracer import Tracer; print('tracer-service ready')"]
