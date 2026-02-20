import gitlab
import pandas as pd
import base64
import json
import re

# =============================
# LOAD CONFIG
# =============================
with open("/mnt/data/config.json") as f:
    config = json.load(f)

gl = gitlab.Gitlab(
    url=config["gitlab_url"],
    private_token=config["access_token"]
)

BRANCH = "your-branch"
CI_FILE = ".gitlab-ci.yml"
EXCEL_FILE = "projects.xlsx"

# =============================
# NEW VARIABLES (insert first)
# =============================
NEW_VARIABLES = [
    "  NEW_VAR1: value1",
    "  NEW_VAR2: value2",
    "  NEW_VAR3: value3",
    "  NEW_VAR4: value4",
]

# =============================
# NEW SCRIPT CONTENT
# =============================
NEW_SCRIPT = [
    "    - echo \"New pipeline started\"",
    "    - echo \"Running new logic\"",
    "    - echo \"Pipeline complete\"",
]

# =============================
# READ EXCEL
# =============================
df = pd.read_excel(EXCEL_FILE)
project_urls = df["Repository URL"].tolist()

# =============================
# PROCESS EACH PROJECT
# =============================
for url in project_urls:
    try:
        print(f"\nProcessing: {url}")

        project_path = url.split("gitlab.com/")[1]
        project = gl.projects.get(project_path)

        file = project.files.get(
            file_path=CI_FILE,
            ref=BRANCH
        )

        content = base64.b64decode(file.content).decode("utf-8")
        lines = content.split("\n")

        updated_lines = []
        i = 0
        variables_inserted = False

        while i < len(lines):
            line = lines[i]

            # =============================
            # INSERT VARIABLES (ONLY ONCE)
            # =============================
            if not variables_inserted and re.match(r"^variables:\s*$", line.strip()):
                updated_lines.append(line)
                updated_lines.extend(NEW_VARIABLES)
                variables_inserted = True
                i += 1
                continue

            # =============================
            # REPLACE SCRIPT BLOCK
            # =============================
            if re.match(r"^\s*script:\s*$", line):
                indent = len(line) - len(line.lstrip())
                script_indent = " " * indent

                # Add new script header
                updated_lines.append(script_indent + "script:")

                # Add new script lines
                updated_lines.extend(NEW_SCRIPT)

                i += 1

                # Skip old script block
                while i < len(lines):
                    next_line = lines[i]

                    # Stop skipping when indentation decreases
                    if next_line.strip() == "":
                        i += 1
                        continue

                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent:
                        break

                    i += 1

                continue

            updated_lines.append(line)
            i += 1

        updated_content = "\n".join(updated_lines)

        file.content = updated_content
        file.save(
            branch=BRANCH,
            commit_message="Update CI: insert variables + replace scripts"
        )

        print("✅ Updated successfully")

    except Exception as e:
        print(f"❌ Failed: {url}")
        print(e)