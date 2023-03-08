from dotenv import load_dotenv
load_dotenv()

import os
import json
from datetime import datetime

from github import Github, GithubException
from tqdm import tqdm

from meta import Meta


if __name__ == '__main__':

    g = Github(os.environ['GITHUB_TOKEN'], timeout=45)

    meta = Meta()

    repos = g.search_repositories('stars:30000..40000')
    for repo in tqdm(repos, total=repos.totalCount):

        # get repo meta
        repo_meta = meta[repo.id]

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

                # get contributor meta
                contributor_meta = repo_meta.contributors[contributor.id]

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

        except GithubException as e:
            print(e)
            rate_limit = g.get_rate_limit().core
            print(f'Rate Limit Reset at {rate_limit.reset}')
            break
        except Exception as e:
            print(e)
        except KeyboardInterrupt:
            print('Interrupted by user.')
        finally:
            # after all repo info has been parsed, save info to a file
            with open(repo_meta.file, 'w') as f:
                json.dump(repo_info, f)

            # update repo meta and save
            meta.info[repo.id] = repo_meta
            completed = meta.check_repo_completion(repo.id)
            if completed:
                print(f'Parsed all info for {repo_info["url"]} repo')
            meta.save()
