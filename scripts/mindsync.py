#!/usr/bin/env python3

import os
import re
import argparse
import requests
import json
import zipfile
import subprocess

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

    if len(r.content):
        return filename

    return None

def send_logs(api, token, hash, logs):
    url = api + '/codes/' + hash + '/log'
    headers = {
        'api-rent-key': token,
    }
    r = requests.post(url, headers=headers, files={'file': (hash + '.log', logs, 'text/plain')})
    return json.loads(r.content)

def send_status(api, token, uuid, execution_id, status, message):
    url = api + '/rents/' + uuid + '/state'
    headers = {
        'api-rent-key': token,
    }
    r = requests.post(url, headers=headers, json={"executionId": execution_id, "name": status, "message": message})
    if len(r.content):
        return json.loads(r.content)   

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mindsync.api', required=True)
    ap.add_argument('--mindsync.token', required=True)
    ap.add_argument('--mindsync.code', required=True)
    ap.add_argument('--mindsync.run', default='not_run', nargs='?')
    ap.add_argument('--mindsync.execution_id', required=False)

    namespace, extra = ap.parse_known_args()
    args = vars(namespace)

    api = args['mindsync.api']
    token = args['mindsync.token']
    code = args['mindsync.code']
    execution_id = args['mindsync.execution_id']
    status = 'code_upload'

    if args['mindsync.run'] is None:
        status = 'code_execute'

    if code:
        config = read_config()
        info = get_info(api, token, code)

        if info['error']:
            print('{"error":"' + info['error']['message'] + '", "success": false}')
            return

        send_status(api, token, config['uuid'], execution_id, status + '_started', 'trying to upload code ' + info['result']['name'] + ' from url ' + info['result']['attachmentLink'])
        code = download(token, info['result']['name'], info['result']['attachmentLink'])

        if code is None:
            send_status(api, token, config['uuid'], execution_id, status + '_failed', 'code upload is failed')
            print('{"error":"code_upload_failed", "success": false}')
            return

        config[code] = info
        config['token'] = token
        config['api'] = api
        save_config(config)

        code_name, code_extension = os.path.splitext(code)
        code_hash = config[code]['result']['hash']

        if code_extension == ".py":
    	    os.system("/opt/conda/bin/p2j " + code)
        
        for dataset in info['result']['datasetList']:
            filename = download(token, dataset['hash'], dataset['zipLink'])
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(WORK_DIR)
            os.unlink(filename)

        if args['mindsync.run'] is None:
            result = subprocess.getoutput('python ' + os.path.join(WORK_DIR, code))
            send_status(api, token, config['uuid'], execution_id, status + '_finished', result)
            send_logs(api, token, code_hash, result)
        else:
            send_status(api, token, config['uuid'], execution_id, status + '_finished', 'download completed')

    print('{"success":true}')

if __name__ == '__main__':
    main()
