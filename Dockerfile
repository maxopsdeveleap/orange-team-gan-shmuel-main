FROM python:3.10

WORKDIR /app

# Install dependencies

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code

COPY . .

# Ensure the repository is cloned when the container starts

RUN git clone https://github.com/maxopsdeveleap/orange-team-gan-shmuel-main /home/ubuntu/orange-team-gan-shmuel-main || true

CMD ["python", "devops/ci/webhook_server.py"]