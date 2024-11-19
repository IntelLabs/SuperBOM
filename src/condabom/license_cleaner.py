import spdx_lookup as lookup
import spdx_matcher


def lookup_license(license):
    # Case-insensitive SPDX name lookup
    licenseinfo = lookup.by_name(license) # -> returns License object or None

    if not licenseinfo:
        match = lookup.match(license) # -> returns License object or None
        if match:
            licenseinfo = match[0][1]

    if not licenseinfo:
        licenses_detected, percent = spdx_matcher.analyse_license_text(license)
        if licenses_detected['licenses']:
            for k in licenses_detected['licenses']:
                licenseinfo = lookup.by_id(k)
                break

    return licenseinfo.name if licenseinfo else license

def get_license_info(package):
    classifier_license = None
    license = None
    licenseinfo = None
    # Get license information from the classifiers
    try:
        classifiers = package["classifiers"]
        for c in classifiers:
            if "License" in c:
                classifier_license = c.split("::")[-1].strip()
                break
    except:
        pass

    # Get license information from the license field
    try:
        license = package["license"]
    except:
        license = "No License Information"
    if classifier_license:
        licenseinfo = lookup_license(classifier_license)

    if not licenseinfo:
        licenseinfo = lookup_license(license)

    if not licenseinfo:
        licenseinfo = "NOASSERTION"

    return licenseinfo
