FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.txt

# Copy application code
COPY app/ app/
COPY static/ static/
COPY main.py .

# Expose port
EXPOSE 8000
USER 65532:65532

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--limit-concurrency", "32", "--timeout-keep-alive", "5"]
