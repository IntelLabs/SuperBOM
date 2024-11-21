from flame.license_db import FossLicenses

def checklicense(license) -> tuple[bool, str]:
    fl = FossLicenses()
    try:
        cleaned_license = fl.license_complete(license)

        expression = fl.expression_compatibility_as(cleaned_license['spdxid'] if cleaned_license else license)

        return expression['compat_support']['supported'], expression['compat_license']
    except:
        return False, license




