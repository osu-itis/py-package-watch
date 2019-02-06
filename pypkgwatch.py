import base64
import github
import os
import requests
import pprint
pp_ = pprint.PrettyPrinter(indent=2)
pp = pp_.pprint


config = {}
config['GITHUB_ENTERPRISE_HOST'] = os.getenv('GITHUB_ENTERPRISE_HOST', '')
config['GITHUB_ENTERPRISE_PAT'] = os.getenv('GITHUB_ENTERPRISE_PAT', '')
config['GITHUB_PAT'] = os.getenv('GITHUB_PAT', '')


def main():
    githubs = []
    if not config['GITHUB_ENTERPRISE_PAT'] == '':
        ghe = github.Github(
            base_url=f"https://{config['GITHUB_ENTERPRISE_HOST']}/api/v3",
            login_or_token=config['GITHUB_ENTERPRISE_PAT']
        )
        githubs.append(ghe)
    if not config['GITHUB_PAT'] == '':
        g = github.Github(config['GITHUB_PAT'])
        githubs.append(g)

    # look for 'requirements.txt' in all repos accessible to this user
    repos = {}
    for g in githubs:
        for repo in g.get_user().get_repos():
            if repo.archived:
                # repo is archived, so skip it
                continue

            try:
                r_file = repo.get_file_contents('requirements.txt')
                r_content = base64.b64decode(r_file.content).decode('utf-8')
            except github.GithubException:
                # repo has no requirements.txt, so skip it
                continue

            for line in r_content.split('\n'):
                if line == '':
                    continue
                (package, version) = line.split('==')
                if not repo.html_url in repos:
                    repos[repo.html_url] = {}
                repos[repo.html_url][package] = version

    # get set of unique package names
    unique_pkgs = set([pkg_name
                       for repo_url, pkgs in repos.items()
                       for pkg_name, version in pkgs.items()])

    # query PyPI for the latest package versions
    latest_pkgs = {}
    for pkg in unique_pkgs:
        pypi = requests.get(f"https://pypi.org/pypi/{pkg}/json")
        latest_pkgs[pkg] = pypi.json()['info']['version']

    # for each python repo, gather outdated packages
    outdated = {}
    for pkg, pkg_version in latest_pkgs.items():
        for repo_url, repo_pkgs in repos.items():
            if pkg in repo_pkgs and not pkg_version == repo_pkgs[pkg]:
                if not repo_url in outdated:
                    outdated[repo_url] = {}
                outdated[repo_url][pkg] = {
                    'current': repo_pkgs[pkg],
                    'latest': pkg_version
                }

    # print result
    for repo_url in sorted(outdated):
        pkgs = outdated[repo_url]
        print(f"\n{repo_url}")
        for pkg in sorted(pkgs, key=lambda item: (item[0].lower())):
            print(f"\t{pkg}: {pkgs[pkg]['current']} != {pkgs[pkg]['latest']}")


if __name__ == '__main__':
    main()
