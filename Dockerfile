FROM python:3.10

WORKDIR /app

# Install system dependencies including Docker CLI and Docker Compose

RUN apt-get update && apt-get install -y \

    curl \

    && curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose \

    && chmod +x /usr/local/bin/docker-compose

# Copy and install Python dependencies

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "devops/ci/webhook_server.py"]