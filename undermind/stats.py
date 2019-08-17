import requests
import json
import time

def post_json_file(index, path, extra):
    try:
        data = json.loads(open(path).read())
        post_dict(index, data, extra)
    except:
        print("[Stats] Couldn't post stats")

def post_dict(index, data, extra):
    try:
        data.update(extra)
        data['timestamp'] = int(time.time() * 1000.0)
        r = requests.post(f'http://localhost:9200/{index}/_doc', json=data)
        if r.status_code != 201:
            print(r)
            print(r.content)
    except:
        print("[Stats] Couldn't post stats")
