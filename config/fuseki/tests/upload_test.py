import requests
import io

url = "https://docker-dev.iwm.fraunhofer.de/fuseki/$/datasets"
filename = "assembly4.ttl"

with open(filename, "r") as f:
    file_data = f.read()

files = {"file": ("assembly.ttl", file_data, "text/turtle", {"Expires": "0"})}

response = requests.post(url, files=files, auth=("admin", "admin"), verify=False)
print(response.text)
print(response.status_code)
