from flask import Flask, request, jsonify
import os
import subprocess
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# Set these variables
GIT_REPO = "https://github.com/maxopsdeveleap/orange-team-gan-shmuel-main"
LOCAL_REPO_PATH = "/home/max/Desktop/tasks_develeap/orange_team/orange_repo/orange-team-gan-shmuel-main"
SERVICES = ["weight", "billing"]

# Zoho Mail Configuration
EMAIL_SENDER = "orange.team.ci@zohomail.com"
EMAIL_PASSWORD = os.getenv("ZOHO_EMAIL_PASSWORD")  # Securely read from environment variable
SMTP_SERVER = "smtp.zoho.com"
SMTP_PORT = 587


@app.route('/webhook', methods=['POST'])
def github_webhook():
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json

    # 🔹 Handle Pull Request Events (Only Run CI After Merge)
    if event_type == "pull_request":
        action = payload.get("action", "")
        branch = payload.get("pull_request", {}).get("base", {}).get("ref", "")

        if action == "closed" and payload.get("pull_request", {}).get("merged", False):
            print(f"✅ PR to {branch} has been merged! Running CI...")
            handle_ci_branch(branch)
            return jsonify({"message": f"CI triggered for merged PR to {branch}"}), 200

        print(f"🔍 PR {action} on {branch} - No CI triggered yet.")
        return jsonify({"message": "No CI triggered, waiting for merge."}), 200

    return jsonify({"message": "Not a pull request event"}), 200


def handle_ci_branch(branch):
    if branch == "main":
        print(f"🚀 Production PR merged into {branch}, running production CI...")
        run_production_pipeline()
        send_email(
            subject=f"🚀 Production Deployment Triggered on {branch}",
            body="Production pipeline has started. You'll receive another email once deployment is complete.",
            receiver="team.notify@zohomail.com"
        )
    else:
        print(f"🔧 Development PR merged into {branch}, running development CI...")
        run_ci_pipeline(branch)
        send_email(
            subject=f"✅ CI Success for {branch}",
            body="CI pipeline completed successfully for your merged PR.",
            receiver="team.notify@zohomail.com"
        )


def pull_latest_code():
    if not os.path.exists(LOCAL_REPO_PATH):
        print(f"Cloning repository {GIT_REPO}...")
        subprocess.run(["git", "clone", GIT_REPO, LOCAL_REPO_PATH], check=True)
    else:
        print(f"Pulling latest changes in {LOCAL_REPO_PATH}...")
        subprocess.run(["git", "-C", LOCAL_REPO_PATH, "fetch"], check=True)
        subprocess.run(["git", "-C", LOCAL_REPO_PATH, "pull"], check=True)


def run_ci_pipeline(branch):
    print(f"🔧 Running CI pipeline for branch: {branch}")

    for service in SERVICES:
        service_path = os.path.join(LOCAL_REPO_PATH, service)
        print(f"➡️ Handling service: {service}")

        subprocess.run(["docker-compose", "build"], cwd=service_path, check=True)
        subprocess.run(["docker-compose", "up", "-d"], cwd=service_path, check=True)

    print("✅ Running E2E tests (placeholder)...")

    for service in SERVICES:
        service_path = os.path.join(LOCAL_REPO_PATH, service)
        print(f"⛔️ Stopping service: {service}")
        subprocess.run(["docker-compose", "down"], cwd=service_path, check=True)

    print("✅ CI pipeline completed successfully.")


def run_production_pipeline():
    print("🚀 Running Production Deployment... (Placeholder)")
    # TODO: Add actual production deployment logic (Docker push, EC2 deploy, etc.)


def send_email(subject, body, receiver):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = receiver

    print(f"📧 Sending email to {receiver} via Zoho...")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Email failed: {e}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
