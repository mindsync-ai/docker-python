#!/bin/bash
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

set -ex

wrapper=""
if [[ "${RESTARTABLE}" == "yes" ]]; then
    wrapper="run-one-constantly"
fi

python /usr/local/bin/custom.py "$@"

ARGS=()
for param in "$@"; do
    name=(${param//=/ }[0])
    ! [[ "${name}" =~ '--mindsync' ]] && ARGS+=("$param")
done

if [[ -n "${JUPYTERHUB_API_TOKEN}" ]]; then
    # launched by JupyterHub, use single-user entrypoint
    exec /usr/local/bin/start-singleuser.sh "${ARGS[@]}"
elif [[ -n "${JUPYTER_ENABLE_LAB}" ]]; then
    # shellcheck disable=SC1091
    . /usr/local/bin/start.sh ${wrapper} jupyter lab "${ARGS[@]}"
else
    echo "WARN: Jupyter Notebook deprecation notice https://github.com/jupyter/docker-stacks#jupyter-notebook-deprecation-notice."
    # copy welcome.ipynb
    git clone https://github.com/mindsync-ai/docker-python-demo
    cp docker-python-demo/welcome.ipynb .
    rm -rf docker-python-demo

    # shellcheck disable=SC1091
    . /usr/local/bin/start.sh ${wrapper} jupyter notebook --NotebookApp.default_url=/notebooks/welcome.ipynb "${ARGS[@]}"
fi
