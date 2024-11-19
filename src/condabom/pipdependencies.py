import base64
import re
import requests

from . import license_cleaner

def get_package_info_github(package):
    info = None
    #extract the repo name from the package string
    package_name = package.split('github.com/')[-1].strip('.git')

    url = f"https://api.github.com/repos/{package_name}"
    response = requests.get(url)
    if response.status_code == 200:
        tmp = response.json()

        info = {
            'name': tmp.get('name', package),
            'version': tmp.get('tag_name', 'N/A'),
            'license': tmp.get('license', {}).get('spdx_id', 'N/A'),
            'source': 'github'
        }

        if "NOASSERTION" in info['license']:
            # try to download the license file
            license_url = url + '/license'
            if license_url:
                license_response = requests.get(license_url)
                if license_response.status_code == 200:
                    license_text = license_response.json().get('content').strip("\n")
                    license_text = base64.b64decode(license_text).decode('utf-8')
                    license = license_cleaner.lookup_license(license_text)
                    info['license'] = license
    else:
        print(f"Failed to fetch data for {package_name}")
    
    return info

def get_package_info_pypi(package_name, release=None):
    info = None
    url = f"https://pypi.org/pypi/{package_name}{f'/{release}' if release else ''}/json"
    response = requests.get(url)
    if response.status_code == 200:
        tmp = response.json()
        package_info = tmp['info']
        return package_info
    else:
        print(f"Failed to fetch data for {package_name}")
        return None
    
def get_pip_packages_data(pip_deps) -> list:
    package_data = []
    info = None
    release = None
    for package in pip_deps:

        if 'github.com' in package:
            info = get_package_info_github(package)
        else:
            try:
                # Split the package string using the pattern
                parts = re.split(r"=|==|>=|<=|!=|~=", package)
                package = parts[0]
                release = parts[1] + parts[2] if len(parts) > 2 else None
            except Exception as e:
                print(f"Failed to split package name and version: {e}")
                package, _ = package, None

            info = get_package_info_pypi(package, release)
            
        if info:
            name = info.get('name', 'N/A')
            version = info.get('version', 'N/A')
            license = license_cleaner.get_license_info(info)
            source = 'pip'

            package_data.append({
                'Package': name,
                'Version': version,
                'License': license,
                'Source': source
            })
            print (f"Package: {name}, Version: {version}, License: {license}, Source: {source}")
    return package_data
