import requests
from condabom.utils.licenseutils import checklicense

def get_license(source):
    if not "github.com" in source:
        source = _search(source)
    return _lookuplicense(source)

def _search(repo_name):
    url = f"https://api.github.com/search/repositories?q={repo_name}+in:name"
    response = requests.get(url)
    if response.status_code == 200:
        repos = response.json()['items']

        for repo in repos:
            if repo['name'] == repo_name:
                return repo['html_url']

    return None

def _lookuplicense(source_url):

    owner, repo = source_url.split("github.com/")[1].split("/")

    url = f"https://api.github.com/repos/{owner}/{repo}/license"
    response = requests.get(url)
    if response.status_code == 200:
        tmp = response.json()

        if tmp.get('license'):
            license = tmp['license']['spdx_id']
            return checklicense(license)

    return False, None
