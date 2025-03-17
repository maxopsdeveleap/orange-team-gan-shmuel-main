from flask import Flask, request, jsonify
import os
import subprocess

app = Flask(__name__)

# Set these variables
GIT_REPO = "https://github.com/maxopsdeveleap/orange-team-gan-shmuel-main"
LOCAL_REPO_PATH = "/home/andishobash/Desktop/orange-team-gan-shmuel-main" 
DOCKER_IMAGE_NAME = "gan-shmuel:latest"

@app.route('/webhook', methods=['POST'])
def github_webhook():
    event_type = request.headers.get('X-GitHub-Event')  # Get event type
    payload = request.json 

    if event_type == "push":  # Check if it's a push event
        repo_name = payload.get("repository", {}).get("name", "Unknown Repo")
        pusher_name = payload.get("pusher", {}).get("name", "Unknown User")

        print(f"🔹 Push detected in repository: {repo_name}")
        print(f"🔹 Pushed by: {pusher_name}")

        pull_latest_code()

        build_docker_image()

        return jsonify({"message": "Push event detected and Docker image built"}), 200

    return jsonify({"message": "Not a push event"}), 200

def pull_latest_code():
    if not os.path.exists(LOCAL_REPO_PATH):
        print(f"Cloning repository {GIT_REPO}...")
        subprocess.run(["git", "clone", GIT_REPO, LOCAL_REPO_PATH], check=True)
    else:
        print(f"Pulling latest changes in {LOCAL_REPO_PATH}...")
        subprocess.run(["git", "-C", LOCAL_REPO_PATH, "pull"], check=True)

def build_docker_image():
    print(f"Building Docker image: {DOCKER_IMAGE_NAME}...")
    subprocess.run(["docker", "build", "-t", DOCKER_IMAGE_NAME, LOCAL_REPO_PATH], check=True)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)