FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install pydantic rich boto3 httpx
COPY safetrace/ ./safetrace/
ENV PYTHONPATH=/app
RUN useradd -m -u 1002 controller
USER controller
CMD ["python", "-c", "from safetrace.controller import Controller; print('controller-service ready')"]
