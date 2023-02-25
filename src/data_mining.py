from dotenv import load_dotenv
load_dotenv()

import os
from datetime import date

from github import Github
from tqdm import tqdm
import pandas as pd


if __name__ == '__main__':

    g = Github(os.environ['GITHUB_TOKEN'], timeout=45)

    data = []
    repos = g.search_repositories('stars:>=100000')
    for repo in tqdm(repos, total=repos.totalCount):
        try:
            repo_info = {}
            repo_info['id'] = repo.id
            repo_info['url'] = repo.url
            repo_info['name'] = repo.name
            repo_info['owner'] = repo.owner.login
            repo_info['stars'] = repo.stargazers_count
            repo_info['commits'] = []
            contributors = repo.get_contributors()
            for contributor in tqdm(contributors, total=contributors.totalCount):
                repo_info['commits'].append({
                    'author_id': contributor.id,
                    'author_url': contributor.url,
                    'author_location': contributor.location,
                    'total_commits': repo.get_commits(author=contributor).totalCount
                })
            data.append(repo_info)
        except Exception as e:
            print(e)

    df = pd.json_normalize(
        data,
        record_path='commits',
        meta=['id', 'url', 'name', 'owner', 'stars'],
        record_prefix='commit_'
    )

    df.to_csv(f'data/conributors_{date.today()}.csv', index=False)
