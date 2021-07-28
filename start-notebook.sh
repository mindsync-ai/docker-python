#!/bin/bash
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

set -e

wrapper=""
if [[ "${RESTARTABLE}" == "yes" ]]; then
    wrapper="run-one-constantly"
fi

python /usr/local/bin/custom.py "$@"

ARGS=()
for param in "$@"; do
    name=(${param//=/ }[0])
    [ "${name}" != '--mindsync.base_url' ] && ARGS+=("$param")
done

if [[ -n "${JUPYTERHUB_API_TOKEN}" ]]; then
    # launched by JupyterHub, use single-user entrypoint
    exec /usr/local/bin/start-singleuser.sh "${ARGS[@]}"
elif [[ -n "${JUPYTER_ENABLE_LAB}" ]]; then
    # shellcheck disable=SC1091
    . /usr/local/bin/start.sh ${wrapper} jupyter lab "${ARGS[@]}"
else
    echo "WARN: Jupyter Notebook deprecation notice https://github.com/jupyter/docker-stacks#jupyter-notebook-deprecation-notice."
    # shellcheck disable=SC1091
    git clone https://github.com/mindsync-ai/docker-python-demo . && rm -rf .git README.md
    . /usr/local/bin/start.sh ${wrapper} jupyter notebook --NotebookApp.default_url=/notebooks/welcome.ipynb "${ARGS[@]}"
fi
