#!/usr/bin/env python3

import os
import argparse
import requests
import json
import zipfile

PATH = '/home/mindsync/work/'

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
        filename = re.findall("filename=\"(.+)\"", r.headers["Content-Disposition"])[0]
    else:
        filename = PATH + name
        
    f = open(filename, "wb")
    f.write(r.content)
    f.close()
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
        info = get_info(api, token, code)

        if info['error']:
            print('{"error":"' + info['error']['message'] + '", "success": false}')
            return

        download(token, info['result']['name'], info['result']['attachmentLink'])
        for dataset in info['result']['datasetList']:
            filename = download(token, dataset['hash'], dataset['zipLink'])
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(PATH)
            os.unlink(filename)

    print('{"success":true}')

if __name__ == '__main__':
    main()
