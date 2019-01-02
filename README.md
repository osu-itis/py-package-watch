# py-package-watch

Report outdated Python packages in GitHub repos

This script searches all repos accessible to the given user accounts on GitHub.com and/or GitHub Enterprise for `requirements.txt` files and generates a list of outdated packages from within those files.

## Requirements

* Python 3.6+
* packages in `requirements.txt`

## Configuration

Configuration is via environment variables:

* `GITHUB_PAT` - [Personal Access Token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) for user account on GitHub
* `GITHUB_ENTERPRISE_HOST` - hostname of GitHub Enterprise instance
* `GITHUB_ENTERPRISE_PAT` - [Personal Access Token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) for user account on GitHub Enterprise
