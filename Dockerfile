# Use a lightweight Python base image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Ensure the Flask server runs continuously
CMD ["python", "devops/ci/webhook_server.py"]
