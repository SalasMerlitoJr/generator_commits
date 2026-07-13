import os
import random
import shutil
import subprocess
from datetime import datetime, timedelta


def get_positive_int(prompt, default=20):
    while True:
        try:
            user_input = input(f"{prompt} (default {default}): ")
            if not user_input.strip():
                return default
            value = int(user_input)
            if value > 0:
                return value
            else:
                print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


def get_repo_path(prompt, default="."):
    while True:
        user_input = input(f"{prompt} (default current directory): ")
        if not user_input.strip():
            return default
        if os.path.isdir(user_input):
            return user_input
        else:
            print("Directory does not exist. Please enter a valid path.")


def get_filename(prompt, default="commit.txt"):
    user_input = input(f"{prompt} (default {default}): ")
    if not user_input.strip():
        return default
    return user_input


def get_folder_name(prompt, default="archive"):
    user_input = input(f"{prompt} (default {default}): ")
    if not user_input.strip():
        return default
    return user_input


def random_date_in_last_year():
    today = datetime.now()
    start_date = today - timedelta(days=365)
    random_days = random.randint(0, 364)
    random_seconds = random.randint(0, 23 * 3600 + 3599)
    commit_date = start_date + timedelta(days=random_days, seconds=random_seconds)
    return commit_date


def make_commit(date, repo_path, filename, message="Wassup Madafaka!"):
    filepath = os.path.join(repo_path, filename)
    with open(filepath, "a") as f:
        f.write(f"Commit at {date.isoformat()}\n")
    subprocess.run(["git", "add", filename], cwd=repo_path)
    env = os.environ.copy()
    date_str = date.strftime("%Y-%m-%dT%H:%M:%S")
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str
    subprocess.run(["git", "commit", "-m", message], cwd=repo_path, env=env)


def organize_into_folder(repo_path, filename, folder_name):
    """
    After pushing, move the commit file into a new folder inside the repo,
    then commit and push that organizational change.
    """
    folder_path = os.path.join(repo_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    src = os.path.join(repo_path, filename)
    if not os.path.isfile(src):
        print(f"⚠️  {filename} not found, skipping organization step.")
        return

    dest = os.path.join(folder_path, filename)

    # Use git mv when possible so history/tracking is preserved
    result = subprocess.run(
        ["git", "mv", filename, os.path.join(folder_name, filename)],
        cwd=repo_path,
    )
    if result.returncode != 0:
        # fallback to plain move + git add if git mv fails (e.g. untracked file)
        shutil.move(src, dest)
        subprocess.run(["git", "add", os.path.join(folder_name, filename)], cwd=repo_path)
        subprocess.run(["git", "add", "-A"], cwd=repo_path)

    commit_result = subprocess.run(
        ["git", "commit", "-m", f"Organize: move {filename} into {folder_name}/"],
        cwd=repo_path,
    )
    if commit_result.returncode == 0:
        print(f"📁 Moved {filename} into {folder_name}/ and committed the change.")
        push = subprocess.run(["git", "push"], cwd=repo_path)
        if push.returncode == 0:
            print("✅ Organization change pushed.")
        else:
            print("⚠️  Could not push the organization change. Push it manually.")
    else:
        print("ℹ️  Nothing to commit for organization step (already organized?).")


def main():
    print("=" * 60)
    print("🌱 Welcome to GitHub Contribution Graph Commit Generator 🌱")
    print("=" * 60)
    print("This tool will help you fill your GitHub contribution graph with custom commits.\n")

    num_commits = get_positive_int("How many commits do you want to make", 20)
    repo_path = get_repo_path("Enter the path to your local git repository", ".")
    filename = get_filename("Enter the filename to modify for commits", "commit.txt")
    folder_name = get_folder_name(
        "Enter the folder name to organize the file into after pushing", "archive"
    )

    print(f"\nMaking {num_commits} commits in repo: {repo_path}\nModifying file: {filename}\n")

    for i in range(num_commits):
        commit_date = random_date_in_last_year()
        print(f"[{i+1}/{num_commits}] Committing at {commit_date.strftime('%Y-%m-%d %H:%M:%S')}")
        make_commit(commit_date, repo_path, filename)

    print("\nPushing commits to your remote repository...")
    subprocess.run(["git", "push"], cwd=repo_path)
    print("✅ All done! Check your GitHub contribution graph in a few minutes.\n")

    print(f"Organizing {filename} into '{folder_name}/' ...")
    organize_into_folder(repo_path, filename, folder_name)

    print("\nTip: Use a dedicated repository for best results. Happy coding!")


if __name__ == "__main__":
    main()