#!/bin/bash

export __dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export __dir="$( dirname ${__dir} )"

if [ -d ${__dir}/__envi ]
then
    . ${__dir}/__envi/bin/activate
    export PYTHONPATH=${__dir}/src
    # ${__dir}/__envi/bin/python -u -m yep -v ${PYTHONPATH}/navi/manual.py $@
else
    echo "Application not installed. Please run \`${__dir}/bin/install.sh\`"
fi