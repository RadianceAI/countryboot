'''
Means for meta information manipulations.
'''
import pickle
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator


@dataclass
class ContributorMeta:
    github_id: int
    collected: bool


@dataclass
class ContributorMetaCollection:
    _contributors: dict[int, ContributorMeta] = field(default_factory=dict)

    def __getitem__(self, contributor_id: int) -> ContributorMeta:
        try:
            return self._contributors[contributor_id]
        except KeyError:
            return ContributorMeta(github_id=contributor_id, collected=False)

    def __setitem__(
        self, contriburor_id: int, contributor: ContributorMeta
    ) -> None:
        self._contributors[contriburor_id] = contributor

    def __iter__(self) -> Iterator[ContributorMeta]:
        return iter(self._contributors.values())


@dataclass
class RepoMeta:
    github_id: int
    file: str
    completed: bool
    last_update: datetime
    contributors: ContributorMetaCollection


class Meta:

    def __init__(self):
        self.fname = os.environ.get('META_FILENAME', 'data/meta.pkl')
        try:
            with open(self.fname, 'rb') as f:
                self.info = pickle.load(f)
        except FileNotFoundError:
            self.info = {}

    def __getitem__(self, repo_id: int) -> RepoMeta:
        try:
            return self.info[repo_id]
        except KeyError:
            return RepoMeta(
            github_id=repo_id,
            file=f'data/{repo_id}.json',
            completed=False,
            last_update=datetime.now(),
            contributors=ContributorMetaCollection()
        )

    def check_repo_completion(self, repo_id: int) -> bool:
        completed = all(
            contributor.collected
            for contributor in self.info[repo_id].contributors
        )
        self.info[repo_id].completed = completed
        return completed

    def save(self):
        with open(self.fname, 'wb') as f:
            pickle.dump(self.info, f)
