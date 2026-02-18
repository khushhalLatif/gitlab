import os
from git import Repo
import xml.etree.ElementTree as ET

REPO_URL = "https://oauth2:YOUR_TOKEN@gitlab.com/group/project.git"
LOCAL_PATH = "repo_clone"
BRANCH = "dev"

# Text to append
GITLAB_APPEND_TEXT = "\n# Added by automation\ninclude:\n  - local: custom.yml\n"

# XML element to append
NEW_XML_TAG = "myElement"
NEW_XML_VALUE = "myValue"


def clone_or_open():
    if not os.path.exists(LOCAL_PATH):
        return Repo.clone_from(REPO_URL, LOCAL_PATH)
    return Repo(LOCAL_PATH)


def update_gitlab_yml(repo_path):
    file_path = os.path.join(repo_path, "gitlab.yml")

    if os.path.exists(file_path):
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(GITLAB_APPEND_TEXT)
        print("✔ Updated gitlab.yml")


def update_pom_xml(repo_path):
    file_path = os.path.join(repo_path, "pom.xml")

    if os.path.exists(file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Add new element at root level
        new_element = ET.Element(NEW_XML_TAG)
        new_element.text = NEW_XML_VALUE
        root.append(new_element)

        tree.write(file_path, encoding="utf-8", xml_declaration=True)
        print("✔ Updated pom.xml")


repo = clone_or_open()
repo.git.checkout(BRANCH)

update_gitlab_yml(LOCAL_PATH)
update_pom_xml(LOCAL_PATH)

repo.git.add(A=True)
repo.index.commit("Automated update: gitlab.yml + pom.xml")
repo.remote("origin").push(BRANCH)

print("✅ Done.")
