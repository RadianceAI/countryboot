# coutryboot

## Description
This is a small data analysis project to explore correlations
between commits that github users make to a project and their location.
"countryboot" is just something that sounds like "contribute"
and does not make any special sense.

## Prerequisites
- Python 3.11
- Poetry

## Install
- run `poetry install`

## Data Mining
Data is being collected through Github API, so you'll need to have [Github Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
You need to make copy of `.env.example` file and call it just `.env` and place your token there.
By default script collects info about repos that have >= 100k stars on Github.
If you want to change that, take a look at `--query` argument.
To run data mining run `sh ./run_data_mining.sh` script in project root.

### CLI args
|Arg|Default value|Description|
|-|-|-|
|-f, --force|false|Forces data retrieval ignoring meta|
|-w, --wait-reset|false|Sleeps until rate limit reset, does not exit|
|-q, --query|"stars:>=100000"|Query for Github repositories search|
