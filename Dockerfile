# Use the official Python image based on Debian slim
FROM python:3.11-slim

# Install system dependencies (including libGL for OpenCV)
RUN apt-get update && apt-get install -y libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port (adjust if necessary)
EXPOSE 8000

# Command to run your Django app (adjust as needed)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
