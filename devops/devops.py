import os
import subprocess

LOCAL_REPO_PATH = "/home/andishobash/Desktop/orange-team-gan-shmuel-main"
commit_id = "90f5eeb"

try:
    result = subprocess.run(
        ["git", "-C", LOCAL_REPO_PATH, "show", "--no-patch", "--pretty=format:%an|%ae", commit_id],
        capture_output=True,
        text=True,
        check=True
    )

    # Extract Name and Email
    output = result.stdout.strip()
    if output:
        github_username, developer_email = output.split("|")
        print(github_username)
        print(developer_email)
    else:
        print("⚠️ No author information found for this commit.")

except subprocess.CalledProcessError as e:
    print(f"❌ Git command failed: {e}")
    print(f"🛠️ Make sure the repository exists and the commit ID is correct.")