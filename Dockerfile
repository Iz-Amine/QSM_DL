# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies


# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV GEMINI_API_KEY=SETUPAFTER

# Expose port (assuming your Flask app runs on port 5000)
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
