FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy demo files
COPY enhanced_demo.html .
COPY demo_server.py .

# Expose port
EXPOSE 8000

# Run the demo server
CMD ["python", "demo_server.py"]