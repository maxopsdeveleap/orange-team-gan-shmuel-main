from flask import Flask, request, jsonify
import os
import subprocess
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# Set these variables
GIT_REPO = "https://github.com/maxopsdeveleap/orange-team-gan-shmuel-main"
LOCAL_REPO_PATH = "/home/andishobash/Desktop/orange-team-gan-shmuel-main"
SERVICES = ["weight", "billing"]
EMAIL_SENDER = "orange_team_gan_shmuel@hotmail.com"   # Replace with your Outlook email
EMAIL_PASSWORD = "maxops123"      # Your Outlook password


@app.route('/webhook', methods=['POST'])
def github_webhook():
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json

    if event_type == "push":
        ref = payload.get("ref", "")
        branch = ref.replace("refs/heads/", "")

        # Extract real developer name and email from head_commit
        pusher_name = payload.get("head_commit", {}).get("author", {}).get("name", "Unknown User")
        pusher_email = payload.get("head_commit", {}).get("author", {}).get("email", "team.notify@outlook.com")  # Fallback if missing

        print(f"🔹 Push detected on branch: {branch} by {pusher_name} ({pusher_email})")

        if branch != "development":
            return jsonify({"message": "Push not on development branch, ignoring."}), 200

        try:
            pull_latest_code()
            run_ci_pipeline(branch)
            send_email(
                subject=f"✅ CI Success for {branch} by {pusher_name}",
                body="CI pipeline completed successfully for your push to development.",
                receiver=pusher_email
            )
            return jsonify({"message": "CI pipeline ran successfully for development"}), 200

        except subprocess.CalledProcessError as e:
            error_message = f"CI pipeline failed: {str(e)}"
            print(f"❌ {error_message}")
            send_email(
                subject=f"❌ CI Failure for {branch} by {pusher_name}",
                body=f"CI pipeline failed for your push to development.\n\nError:\n{error_message}",
                receiver=pusher_email
            )
            return jsonify({"message": "CI pipeline failed", "error": str(e)}), 500

    return jsonify({"message": "Not a push event"}), 200


def pull_latest_code():
    if not os.path.exists(LOCAL_REPO_PATH):
        print(f"Cloning repository {GIT_REPO}...")
        subprocess.run(["git", "clone", GIT_REPO, LOCAL_REPO_PATH], check=True)
    else:
        print(f"Pulling latest changes in {LOCAL_REPO_PATH}...")
        subprocess.run(["git", "-C", LOCAL_REPO_PATH, "pull"], check=True)


def run_ci_pipeline(branch):
    print(f"🔧 Running CI pipeline for branch: {branch}")

    for service in SERVICES:
        service_path = os.path.join(LOCAL_REPO_PATH, service)
        print(f"➡️ Handling service: {service}")

        subprocess.run(["docker-compose", "build"], cwd=service_path, check=True)
        subprocess.run(["docker-compose", "up", "-d"], cwd=service_path, check=True)

    # Placeholder for E2E tests
    print("✅ Running E2E tests (placeholder)...")
    # TODO: Add real tests here later

    for service in SERVICES:
        service_path = os.path.join(LOCAL_REPO_PATH, service)
        print(f"⛔️ Stopping service: {service}")
        subprocess.run(["docker-compose", "down"], cwd=service_path, check=True)

    print("✅ CI pipeline completed successfully.")


def send_email(subject, body, receiver):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = receiver

    print(f"📧 Sending email to {receiver} via Outlook...")

    # Connect to Outlook SMTP server with STARTTLS
    with smtplib.SMTP('smtp.office365.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()  # Secure connection
        smtp.ehlo()
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("✅ Email sent successfully.")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
