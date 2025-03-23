# Use the official Python image based on Debian slim
FROM python:3.11-slim

# Install system dependencies (libGL for OpenCV, libzbar for QR scanning, gcc for compiling packages)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libzbar0 \
    libzbar-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Django will run on
EXPOSE 8000

# Run the Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
