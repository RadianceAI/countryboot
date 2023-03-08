import os
import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from github import Github, GithubException
from tqdm import tqdm
from dotenv import load_dotenv

from meta import Meta
from parse import parse_contributor, parse_repo

load_dotenv()

logging.basicConfig(level=logging.INFO)

GITHUB_TIMEOUT = 45
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
if not GITHUB_TOKEN:
    raise RuntimeError(
        'Github token is not specified, \
        please make sure to include it in GITHUB_TOKEN variable in .env file'
    )
GITHUB_QUERY = 'stars:>=100000'


if __name__ == '__main__':

    logger = logging.getLogger('data_mining')
    logger.setLevel(logging.INFO)

    g = Github(GITHUB_TOKEN, timeout=GITHUB_TIMEOUT)

    meta = Meta()

    repos = g.search_repositories(GITHUB_QUERY)
    for repo in tqdm(repos, total=repos.totalCount):

        # get repo meta
        repo_meta = meta[repo.id]

        # skip repo if it is already parsed
        if repo_meta.completed:
            continue

        try:

            # parse repo info
            repo_info = parse_repo(repo)

            contributors = repo.get_contributors()
            repo_meta.contributors_count = contributors.totalCount
            for contributor in tqdm(
                contributors, total=contributors.totalCount
            ):

                # get contributor meta
                contributor_meta = repo_meta.contributors[contributor.id]

                # skip if contributor already parsed
                if contributor_meta.collected:
                    continue

                # parse contributor info
                repo_info['contributors'].append(
                    parse_contributor(repo, contributor)
                )

                # set contributor meta as collected
                contributor_meta.collected = True

                # update contributor meta in repo meta
                repo_meta.contributors[contributor_meta.github_id] = \
                    contributor_meta
                repo_meta.last_update = datetime.now()

        except GithubException as e:
            logger.error(e)
            reset = g.get_rate_limit().core.reset
            reset = reset.replace(tzinfo=ZoneInfo('UTC'))
            reset = reset.astimezone(ZoneInfo('localtime'))
            logger.info(f'Rate Limit Reset at {reset}')
            break

        except Exception as e:
            logger.error(e)

        except KeyboardInterrupt:
            logger.info('Interrupted by user.')
            break

        finally:
            # after all repo info has been parsed, save info to a file
            with open(repo_meta.file, 'w') as f:
                json.dump(repo_info, f)

            # update repo meta and save
            meta.info[repo.id] = repo_meta
            completed = meta.check_repo_completion(repo.id)
            if completed:
                logger.info(f'Parsed all info for {repo_info["url"]} repo')
            meta.save()
