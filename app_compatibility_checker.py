## THE SCRIPT CHECKS ALL AVAILABLE VERSIONS STARTING FROM THE LATEST AND MOVES TO OLDER VERSIONS IF NECESSARY UNTIL A COMPATIBLE ONE IS FOUND.
import requests
import csv

# RETRIEVES ALL VERSIONS OF AN APP AND IDENTIFIES THE FIRST ONE COMPATIBLE WITH A SPECIFIED SPLUNK VERSION.
def get_compatible_version(app_id, splunk_version):
    url = f"https://splunkbase.splunk.com/api/v1/app/{app_id}/release/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for version_info in data:
            version = version_info["name"]
            compatible_versions = version_info["product_versions"]
            if splunk_version.split(".")[0:2] in [v.split(".")[0:2] for v in compatible_versions]:
                return version, True
    return None, False

def main():
    # APPS LIST SAMPLE -> CHANGE ME
    apps = [
        {"name": "Splunk Add-on for Apache", "splunkbase_url": "https://splunkbase.splunk.com/app/3186"},
        {"name": "Splunk Add-on for AWS", "splunkbase_url": "https://splunkbase.splunk.com/app/5304"},
        {"name": "Splunk Add-on for Microsoft Windows", "splunkbase_url": "https://splunkbase.splunk.com/app/742"},
        {"name": "Splunk Add-on for Oracle", "splunkbase_url": "https://splunkbase.splunk.com/app/1910"},
        {"name": "Splunk Add-on for Unix and Linux", "splunkbase_url": "https://splunkbase.splunk.com/app/833"},
        {"name": "Splunk App for AWS", "splunkbase_url": "https://splunkbase.splunk.com/app/5304"},
        {"name": "Splunk App For Jenkins", "splunkbase_url": "https://splunkbase.splunk.com/app/3332"},
        {"name": "Splunk App for Lookup File Editing", "splunkbase_url": "https://splunkbase.splunk.com/app/1724"},
        {"name": "Splunk Common Information Model", "splunkbase_url": "https://splunkbase.splunk.com/app/1621"},
        {"name": "Splunk DB Connect", "splunkbase_url": "https://splunkbase.splunk.com/app/2686"},
        {"name": "Splunk Machine Learning Toolkit", "splunkbase_url": "https://splunkbase.splunk.com/app/2890"},
        {"name": "Splunk Add-on for Blue Coat ProxySG", "splunkbase_url": "https://splunkbase.splunk.com/app/2758"},
        {"name": "Splunk Add-on for F5 BIG-IP", "splunkbase_url": "https://splunkbase.splunk.com/app/2680"},
        {"name": "Splunk Add-on for Infrastructure", "splunkbase_url": "https://splunkbase.splunk.com/app/4217"},
        {"name": "Splunk Add-on for Microsoft Cloud Services", "splunkbase_url": "https://splunkbase.splunk.com/app/3110"},
        {"name": "Splunk Add-on for Microsoft IIS", "splunkbase_url": "https://splunkbase.splunk.com/app/3185"},
        {"name": "Splunk Add-on for Microsoft SQL Server", "splunkbase_url": "https://splunkbase.splunk.com/app/2648"},
        {"name": "Splunk App for Infrastructure", "splunkbase_url": "https://splunkbase.splunk.com/app/4217"},
        {"name": "Splunk Assessment Tool", "splunkbase_url": "https://splunkbase.splunk.com/app/7419"},
    ]

    # SPLUNK VERSION -> CHANGE ME
    splunk_version = "9.1.5"

    # EXPORTS THE RESULTS TO A CSV FILE WITH COLUMNS FOR APP NAME, LATEST COMPATIBLE VERSION, AND A BOOLEAN INDICATING COMPATIBILITY. -> REMEMBER TO CHANGE THE TARGET PATH IF NEEDED
    with open('splunk_apps_compatibility.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["app_name", "latest_compatible_version", "is_compatible"])

        for app in apps:
            app_id = app["splunkbase_url"].split("/")[-1]
            compatible_version, is_compatible = get_compatible_version(app_id, splunk_version)
            if compatible_version:
                writer.writerow([app["name"], compatible_version, is_compatible])
            else:
                writer.writerow([app["name"], "No compatible version found", False])

if __name__ == "__main__":
    main()
