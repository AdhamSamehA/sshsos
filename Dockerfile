# Use the official Python image as the base
FROM python:3.11-slim

# Set environment variables to prevent Python from writing pyc files and to buffer output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy the requirements file from server/ and install dependencies
COPY server/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip --no-cache-dir
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the port your server runs on
EXPOSE 5200

# Command to start the FastAPI app with Uvicorn
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "5200", "--reload"]