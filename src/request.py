import json
import requests

def fetch_json_from_url(url):
    request = requests.get(url)
    if(request.status_code == 200):
        json_data = json.loads(request.content)
        return json_data
