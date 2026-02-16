import pandas as pd
import gitlab
import json
from urllib.parse import urlparse

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

GITLAB_URL = config["gitlab_url"]
ACCESS_TOKEN = config["access_token"]

# Connect to GitLab
gl = gitlab.Gitlab(GITLAB_URL, private_token=ACCESS_TOKEN)

# Read Excel file
df = pd.read_excel("repos.xlsx")

SOURCE_BRANCH = "BAU"
NEW_BRANCH = "DEV"

def extract_project_path(repo_url):
    parsed = urlparse(repo_url)
    return parsed.path.lstrip("/")  # remove leading slash

for index, row in df.iterrows():
    repo_url = row["Repository URL"]
    project_path = extract_project_path(repo_url)

    try:
        print(f"\nProcessing: {project_path}")
        project = gl.projects.get(project_path)

        # Check if DEV already exists
        try:
            project.branches.get(NEW_BRANCH)
            print(f"⚠ Branch '{NEW_BRANCH}' already exists. Skipping.")
            continue
        except gitlab.exceptions.GitlabGetError:
            pass

        # Create DEV from BAU
        project.branches.create({
            'branch': NEW_BRANCH,
            'ref': SOURCE_BRANCH
        })

        print(f"✅ Created '{NEW_BRANCH}' from '{SOURCE_BRANCH}'")

    except Exception as e:
        print(f"❌ Error processing {project_path}: {e}")

print("\nDone.")
