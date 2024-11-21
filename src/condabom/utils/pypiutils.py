import string
import condabom.utils.githubutils as githubutils
from condabom.utils.licenseutils import checklicense

license_attribute = {
    "license_expression",
    "license"
}

def _get_license_from_metadata(metadata):
    license = None
    
    for attr in license_attribute:
        if metadata.get(attr):
            tmp = metadata.get(attr)
            return checklicense(tmp)

    return None, False

def _get_license_from_classifiers(metadata):
    if metadata.get('classifiers'):
        classifiers = metadata.get('classifiers')
        for c in classifiers:
            if "License" in c:
                tmp = c.split("::")[-1].strip()
                return checklicense(tmp)
    
    return None, False

sourcename_map = {
    "repository",
    "sourcecode",
    "github",
    "source"
}

def _normalize_label(label: str) -> str:
    chars_to_remove = string.punctuation + string.whitespace
    removal_map = str.maketrans("", "", chars_to_remove)
    return label.translate(removal_map).lower()

def _get_license_from_source(metadata):

    if metadata.get('project_urls'):
        project_urls = metadata.get('project_urls')

        # Normalize the keys and get the "source" URL from project_urls
        for key in project_urls.keys():
            normalized_label = _normalize_label(key)
            if normalized_label in sourcename_map:
                source_url = project_urls[key].strip("/")
                return githubutils.get_license(source_url)

    return None, False

def get_license(metadata):

    license_checks = [
        _get_license_from_metadata,
        _get_license_from_classifiers,
        _get_license_from_source
    ]

    results = []

    if metadata:
        for check_func in license_checks:
            valid, license = check_func(metadata)
            if valid:
                return valid, license
            else:
                if not license in results and license:
                    results.append(license)

    # arbitrarily return the last invalid license found
    return False, results[-1] if results else None