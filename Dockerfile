FROM python:3.12.9-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x /app/wait-for-it.sh

CMD ["/app/wait-for-it.sh", "elasticsearch:9200", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
