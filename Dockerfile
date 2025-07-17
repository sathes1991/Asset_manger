FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code (including data folder)
COPY . .

# Ensure /app/data exists and has write permissions
RUN chmod -R 777 /app/data

EXPOSE 5000
CMD ["python", "app.py"]
