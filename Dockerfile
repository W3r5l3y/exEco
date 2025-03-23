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

# Run commands: migrate, load fixtures, start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py load_fixtures && python manage.py runserver 0.0.0.0:8000"]
