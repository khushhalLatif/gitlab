data = {
    'branch': BRANCH,
    'commit_message': 'Update CI: insert variables + replace scripts',
    'actions': [
        {
            'action': 'update',
            'file_path': '.gitlab-ci.yml',
            'content': new_content,
        }
    ]
}

commit = project.commits.create(data)
commit_sha = commit.id

# Cherry pick
project.commits.cherry_pick(commit_sha, branch="target-branch-name")