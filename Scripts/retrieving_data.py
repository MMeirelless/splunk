import requests
import json 
import time
import xml.etree.ElementTree as ET
import urllib3

# Suprime warnings de InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

token = "<TOKEN>"
base_url = "https://<DNS>:8089/"
search_endpoint = "services/search/jobs"
headers = {
    'Authorization': f'Splunk {token}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Creating Search. Customize as needed.
data = {
    'search': '<SEARCH>',
    'earliest_time':'-24h',
    'latest_time':'now',
    'max_time':'120'
}

response = requests.post(base_url + search_endpoint, data=data, headers=headers, verify=False)
root = ET.fromstring(response.text)
sid = root.find('sid').text
print(f"Job SID: {sid}")

# Checking Search Status Every 5 Seconds
status_endpoint = f"services/search/jobs/{sid}"
while True:
    status_response = requests.get(base_url + status_endpoint, headers=headers, verify=False)
    status_root = ET.fromstring(status_response.text)
    dispatch_state = status_root.find(".//{http://dev.splunk.com/ns/rest}key[@name='dispatchState']").text
    print(f"Current Dispatch State: {dispatch_state}")
    
    if dispatch_state == "DONE":
        break
    time.sleep(5)

# Getting Search Results
results_endpoint = f"services/search/jobs/{sid}/results?output_mode=json"
results_response = requests.get(base_url + results_endpoint, headers=headers, verify=False)
results_content = results_response.json()

# Saving Results
with open(f"./data_{sid}.json", "w") as data:
    data.write(json.dumps(results_content, indent=4))
    data.close()
