import gitlab
import json
import csv
import sys
from pathlib import Path

CONFIG_FILE = "config.json"

# ----------------------------
# Load config
# ----------------------------
if not Path(CONFIG_FILE).exists():
    print("❌ config.json not found")
    sys.exit(1)

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

GITLAB_URL = config.get("gitlab_url")
TOKEN = config.get("access_token")
GROUP_PATH = config.get("group_path")

if not all([GITLAB_URL, TOKEN, GROUP_PATH]):
    print("❌ config.json missing required fields")
    sys.exit(1)

# ----------------------------
# Connect to GitLab
# ----------------------------
try:
    gl = gitlab.Gitlab(GITLAB_URL, private_token=TOKEN)
    gl.auth()
    print("✅ GitLab connection successful")
except Exception as e:
    print(f"❌ GitLab connection failed: {e}")
    sys.exit(1)

# ----------------------------
# CSV storage
# ----------------------------
rows = []
max_depth = 0


def add_project(project, parents):
    global max_depth
    max_depth = max(max_depth, len(parents))
    rows.append({
        "component_name": project.name,
        "url": project.web_url,
        "parents": parents.copy()
    })


# ----------------------------
# Recursive traversal
# ----------------------------
def walk_group(group, parents):
    # Projects in this group
    for project in group.projects.list(all=True):
        add_project(project, parents + [group.name])

    # Subgroups
    for subgroup_info in group.subgroups.list(all=True):
        subgroup = gl.groups.get(subgroup_info.id)
        walk_group(subgroup, parents + [group.name])


# ----------------------------
# Start traversal
# ----------------------------
try:
    root_group = gl.groups.get(GROUP_PATH)
except Exception as e:
    print(f"❌ Unable to access group '{GROUP_PATH}': {e}")
    sys.exit(1)

walk_group(root_group, [])

# ----------------------------
# Write CSV
# ----------------------------
csv_file = "gitlab_projects.csv"

headers = ["component_name", "url"]
headers.extend([f"parent_{i+1}" for i in range(max_depth)])

with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()

    for row in rows:
        record = {
            "component_name": row["component_name"],
            "url": row["url"]
        }

        for i in range(max_depth):
            record[f"parent_{i+1}"] = row["parents"][i] if i < len(row["parents"]) else ""

        writer.writerow(record)

print(f"📄 CSV created: {csv_file}")
print(f"📦 Total projects exported: {len(rows)}")
