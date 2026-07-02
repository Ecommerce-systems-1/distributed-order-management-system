    FROM python:3.11-slim
    WORKDIR /app
    COPY backend/requirements.txt .
    RUN pip install -r requirements.txt
    COPY backend/app ./app
    COPY frontend/out ./frontend/out
    RUN mkdir -p /data
    EXPOSE 7860
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]