
import re
from superbom.utils import condacache, pypiutils
from superbom.utils import licenseutils
from superbom.utils.logger import AppLogger
logger = AppLogger().get_logger()

class CondaPackageUtil:
    def __init__(self):
        self._cache = condacache.CondaCache()


    def parse_conda_dependency(self, dependency):
        # Regular expression to match the dependency pattern
        pattern = re.compile(r'(?:(?P<channel>[^:]+)::)?(?P<package>[^=<>!]+)'
                            r'(?:(?P<version>[=<>!~*]+[^=<>!]+))?'
                            r'(?:(?P<build>=\w+))?')

        match = pattern.match(dependency)
        if not match:
            raise ValueError(f"Invalid dependency format: {dependency}")

        components = match.groupdict()

        # Clean up the version string
        if components.get('version'):
            components['version'] = components['version'].strip(' =<>!~*')

        # Clean up the channel string
        if components.get('channel'):
            components['channel'] = components['channel'].strip()

        # Clean up the package string
        if components.get('package'):
            components['package'] = components['package'].strip()
            
        return components
    
    def lookup_package(self, channel, platform, package, version=None):
        data = self._cache.get_cache(channel, platform)

        if not data:
            logger.error(f"Failed to find cache for {channel}/{platform}")
            return None

        packages = {**data['packages'], **data['packages.conda']}

        try:
            if version is None:
                items = {k: v for k, v in packages.items() if v['name'] == package}
            else:
                items = {k: v for k, v in packages.items() if v['name'] == package and version in v['version']}

            # sort the items by version
            items = sorted(items.items(), key=lambda x: x[1]['version'], reverse=True)
            package_info = items[0] if items else None
        except KeyError:
            pass
        return package_info

    def _find_license(self, dictionary, license):
        for key in dictionary.keys():
            if license in key:
                return key, dictionary[key]
        return None, None

    def retrieve_conda_package_info(self, deps) -> list:
        package_data = []
        for package in deps:
            #make sure there's a package name
            if not package:
                continue
            
            parsed = self.parse_conda_dependency(package)

            for channel in self._cache.channels:
                package_info = {}

                for platform in self._cache.platforms:
                    channel = parsed['channel'] if parsed['channel'] else channel
                    info = self.lookup_package(channel, platform, parsed['package'], parsed['version'])
                    if not info:
                        info = self.lookup_package(channel, platform, parsed['package'])

                    if not info:
                        info = self.lookup_package(channel, platform, f"{parsed['package']}_{platform}")

                    package_info = info[1] if info else None

                    if package_info:
                        # Found the package in the platform
                        _, license_info = self._find_license(package_info, 'license')

                        if license_info:
                            break
                        else:
                            continue

                if package_info:
                    # Found the package in the channel
                    break    

            if not package_info:
                logger.debug(f"Failed to find package: {parsed['package']} in all channels")
                package_info = {}

            name = package_info.get('name', parsed['package'])
            version = package_info.get('version', parsed['version'])

            _, license_info = self._find_license(package_info, 'license')

            if license_info:
                validated, license = licenseutils.checklicense(license_info)

                # if not validated, check PyPI to see if we can find the license
                if not validated:
                    validated, license = pypiutils.get_license(package_info)
            else:
                validated, license = False, 'No License Information'

            package_data.append({
                'Package': name,
                'Version': version,
                'License': license,
                'Validated': validated,
                'Source': f"{channel}:{platform}"
            })

            logger.info(f"Package: {name}, Version: {version}, License: {license}, Source: {channel}:{platform}")

        return package_data

def main():
    dependencies = [
        # 'conda-forge::python=3.8',
        # 'conda-forge::setuptools=59.5.0',
        # 'conda-forge::pip=24.0',
        # 'conda-forge::openmm=7.5.1',
        # 'conda-forge::pdbfixer=1.7',
        'conda-forge::cudatoolkit==11.3.*',
        # 'conda-forge::einops==0.3.2',
        # 'conda-forge::fairscale==0.4.6',
        # 'conda-forge::omegaconf=2.3.0',
        # 'conda-forge::hydra-core=1.3.2',
        # 'conda-forge::pandas=1.3.5',
        # 'conda-forge::pytest=7.4.4',
        # 'bioconda::hmmer==3.3.2',
        # 'bioconda::hhsuite==3.3.0',
        # 'bioconda::kalign2==2.04',
    ]

    package_util = CondaPackageUtil()
    package_util._cache.add_platform('linux-64')
    package_data = package_util.retrieve_conda_package_info(dependencies)

if __name__ == "__main__":
    main()
