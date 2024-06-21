import os
import json
from files import *

def load_json(json_file):
    if not os.path.exists(json_file):
        print('input json file: {} not exist, please check.'.format(json_file))
        return ''
    else:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_str = json.load(f)
        f.close()
        return json_str


def dump_json(json_file, content):
    if content is None:
        print('input is None, please check')
    else:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(content, f)
        f.close()


def is_json(json_str):
    try:
        json.loads(json_str)
        return True
    except Exception as e:
        print('{} accur error:{}'.format(json_str, e))
        return False

def load_json_list(file):
    ret_list = []
    if not os.path.exists(file):
        print('{} not exist'.format(file))
    else:
        ret_list = read_file(file)
        ret_list = [json.loads(e) for e in ret_list if is_json(e)]
    return ret_list
