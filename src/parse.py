from github.Repository import Repository
from github.NamedUser import NamedUser


def parse_repo(repo: Repository) -> dict:
    return {
        'id': repo.id,
        'url': repo.url,
        'name': repo.name,
        'owner': repo.owner.login,
        'stars': repo.stargazers_count,
        'commits': []
    }


def parse_contributor(repo: Repository, contributor: NamedUser) -> dict:
    return {
        'author_id': contributor.id,
        'author_url': contributor.url,
        'author_location': contributor.location,
        'total_commits': repo.get_commits(author=contributor).totalCount
    }
