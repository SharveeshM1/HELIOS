FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

ENV PYTHONPATH=/app/backend

COPY backend /app/backend
COPY ops /app/ops

EXPOSE 8000

CMD ["uvicorn", "backend.server:app", "--app-dir", "/app/backend", "--host", "0.0.0.0", "--port", "8000"]
