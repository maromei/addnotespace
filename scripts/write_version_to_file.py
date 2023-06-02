import os
from pathlib import Path

import git

PROJECT_ROOT = Path(os.path.abspath(__file__)).parent.parent
VERSION_FILE = PROJECT_ROOT / "src/__about__.py"

repo = git.Repo(PROJECT_ROOT)
tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)

latest_tag = str(tags[-1])
if latest_tag[0] == "v":
    latest_tag = latest_tag[1:]

with open(VERSION_FILE, "w") as f:
    f.write(f'__version__ = "{latest_tag}"')
