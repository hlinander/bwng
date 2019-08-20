import requests
import json
import time
from args import args

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
        r = requests.post(f'http://{args.db_host}:9200/{index}/_doc', json=data)
        if r.status_code != 201:
            print(r)
            print(r.content)
    except Exception as e:
        print(str(e))
        print("[Stats] Couldn't post stats")

def delete_index(index):
    r = requests.delete(f'http://{args.db_host}:9200/{index}')
    if r.status_code != 201:
        print(r)
        print(r.content)

def index_type(index, data):
    new_data = {
        'mappings': {
            '_doc': {
                'properties': data
            }
        }
    }
    r = requests.put(f'http://{args.db_host}:9200/{index}', json=new_data)
    if r.status_code != 201:
        print(r)
        print(r.content)
