#!/usr/bin/env python3

import os
import re
import argparse
import requests
import json
import zipfile


WORK_DIR = os.environ['HOME']
CONFIG = '/tmp/mindsync.json'


def read_config():
    try:
        with open(CONFIG) as f:
            return json.load(f)
    except:
        return dict()


def save_config(config):
    with open(CONFIG, 'w', encoding='utf8') as f:
        json.dump(config, f)


def get_info(api, token, hash):
    url = api + '/codes/' + hash
    headers = {
        'api-rent-key': token,
    }
    r = requests.get(url, headers=headers)
    return json.loads(r.content)


def download(token, name, link):
    headers = {
        'api-rent-key': token,
    }
    r = requests.get(link, headers=headers)
    
    if r.headers['Content-Disposition']:
        filename = os.path.join(WORK_DIR, re.findall("filename=\"(.+)\"", r.headers["Content-Disposition"])[0])
    else:
        filename = os.path.join(WORK_DIR, name)

    with open(filename, 'wb') as f:
        f.write(r.content)

    return filename


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mindsync.api', required=True)
    ap.add_argument('--mindsync.token', required=True)
    ap.add_argument('--mindsync.code', required=True)
    args = vars(ap.parse_args())

    api = args['mindsync.api']
    token = args['mindsync.token']
    code = args['mindsync.code']

    if code:
    
        config = read_config()
        
        info = get_info(api, token, code)

        if info['error']:
            print('{"error":"' + info['error']['message'] + '", "success": false}')
            return

        filename = download(token, info['result']['name'], info['result']['attachmentLink'])

        config[filename] = info
        config['token'] = token
        config['api'] = api        
        save_config(config)
        
        for dataset in info['result']['datasetList']:
            filename = download(token, dataset['hash'], dataset['zipLink'])
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(WORK_DIR)
            os.unlink(filename)

    print('{"success":true}')

if __name__ == '__main__':
    main()
