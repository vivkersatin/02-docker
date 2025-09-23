# c:\learn2\02-docker\Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables for the database
ENV DB_URL="postgres://user:password@db:5432/fastapi_db"
# IMPORTANT: Change this to a strong, random key in production!
ENV SECRET_KEY="your-secret-key"

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]