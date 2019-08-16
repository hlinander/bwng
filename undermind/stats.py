import requests
import json

def post_json_file(index, path, extra):
    try:
        data = json.loads(open(path).read())
        post_dict(index, data, extra)
    except:
        print("[Stats] Couldn't post stats")

def post_dict(index, data, extra):
    try:
        all_data = data.update(extra)
        requests.post(f'http://localhost:9200/{index}/_doc', json=all_data)
    except:
        print("[Stats] Couldn't post stats")
