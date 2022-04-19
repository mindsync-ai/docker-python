#!/usr/bin/env python

import os
import json
import argparse
import re, shutil, tempfile

CONFIG = '/tmp/mindsync.json'

def sed_inplace(filename, pattern, repl):
    '''
    Perform the pure-Python equivalent of in-place `sed` substitution: e.g.,
    `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`.
    '''
    # For efficiency, precompile the passed regular expression.
    pattern_compiled = re.compile(pattern)

    # For portability, NamedTemporaryFile() defaults to mode "w+b" (i.e., binary
    # writing with updating). This is usually a good thing. In this case,
    # however, binary writing imposes non-trivial encoding constraints trivially
    # resolved by switching to text writing. Let's do that.
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        with open(filename) as src_file:
            for line in src_file:
                tmp_file.write(pattern_compiled.sub(repl, line))
                print(pattern_compiled.sub(repl, line))

    # Overwrite the original file with the munged temporary file in a
    # manner preserving file attributes (e.g., permissions).
    shutil.copystat(filename, tmp_file.name)
    shutil.move(tmp_file.name, filename)

def save_config(config):
    with open(CONFIG, 'w', encoding='utf8') as f:
        json.dump(config, f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-NotebookApp.base_url", "--NotebookApp.base_url", required=True)
    ap.add_argument("-NotebookApp.token", "--NotebookApp.token", required=False)
    ap.add_argument("-NotebookApp.allow_origin", "--NotebookApp.allow_origin", required=False)
    ap.add_argument('--mindsync.base_url', required=True)
    ap.add_argument('--mindsync.execution_id', required=False)

    namespace, extra = ap.parse_known_args()
    args = vars(namespace)

    uuid = args["NotebookApp.base_url"].split("/")[2]
    base_url = args['mindsync.base_url']

    command = f'wget -O /dev/null -o /dev/null {base_url}/api/1.0/rents/service/status/{uuid}'
    os.system("( crontab -l | grep -v -F \"" + command + "\" ; echo \"*/15 * * * * " + command + "\" ) | crontab -")

    custom_js_fn = os.path.join(os.environ['HOME'], '.jupyter/custom/custom.js')
    sed_inplace(custom_js_fn, '{uuid}', f'{uuid}')
    sed_inplace(custom_js_fn, '{base_url}', f'{base_url}')

    config = dict() 
    config['uuid'] = uuid
    config['base_url'] = base_url
    save_config(config) 

if __name__ == '__main__':
    main()
