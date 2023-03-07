'''
Means for meta information manipulations.
'''
import json
import os
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ContributorMeta:
    github_id: int
    collected: bool


@dataclass
class RepoMeta:
    github_id: int
    file: str
    completed: bool
    last_update: datetime
    contributors: list[ContributorMeta]


class Meta:

    def __init__(self):
        self.fname = os.environ.get('META_FILENAME', 'data/meta.json')
        with open(self.fname, 'r') as f:
            self.info = json.load(f)

    def check_repo_completion(self, repo_id: int) -> bool:
        completed = all(
            contributor.collected
            for contributor in self.info[repo_id].contributors
        )
        self.info[repo_id].completed = completed
        return completed

    def save(self):
        with open(self.fname, 'w') as f:
            json.dump(self.info, f)
