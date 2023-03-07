from dotenv import load_dotenv
load_dotenv()

import os
import json
from datetime import datetime

from github import Github, GithubException
from tqdm import tqdm
import pandas as pd

from meta import Meta, RepoMeta, ContributorMeta


if __name__ == '__main__':

    g = Github(os.environ['GITHUB_TOKEN'], timeout=45)

    meta = Meta()

    repos = g.search_repositories('stars:>=100000')
    for repo in tqdm(repos, total=repos.totalCount):

        # get repo meta or create new
        repo_meta = meta.get(repo.id, RepoMeta(
            github_id=repo.id,
            file=f'data/{repo.id}.json',
            completed=False,
            last_update=datetime.now(),
            contributors={}
        ))

        # skip repo if it is already parsed
        if repo_meta.completed:
            continue

        try:

            # parse repo info
            repo_info = {}
            repo_info['id'] = repo.id
            repo_info['url'] = repo.url
            repo_info['name'] = repo.name
            repo_info['owner'] = repo.owner.login
            repo_info['stars'] = repo.stargazers_count
            repo_info['commits'] = []
            contributors = repo.get_contributors()

            for contributor in tqdm(contributors, total=contributors.totalCount):

                # get contributor meta or create new
                contributor_meta = repo_meta.contributors.get(
                    contributor.id,
                    ContributorMeta(github_id=contributor.id, collected=False)
                )

                # skip if contributor already parsed
                if contributor_meta.collected:
                    continue

                # parse contributor info
                repo_info['commits'].append({
                    'author_id': contributor.id,
                    'author_url': contributor.url,
                    'author_location': contributor.location,
                    'total_commits': repo.get_commits(author=contributor).totalCount
                })

                # set contributor meta as collected
                contributor_meta.collected = True

                # update contributor meta in repo meta
                repo_meta.contributors[contributor_meta.github_id] = contributor_meta
                repo_meta.last_update = datetime.now()

            # after all repo info has been parsed, save info to a file
            with open(repo_meta.file, 'w') as f:
                json.dump(repo_info, f)

            # update repo meta and save
            meta.info[repo.id] = repo_meta
            meta.check_repo_completion(repo.id)
            meta.save()

        except GithubException as e:
            pass
        except Exception as e:
            print(e)
