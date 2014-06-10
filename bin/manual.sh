#!/bin/bash

export __dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export __dir="$( dirname ${__dir} )"

usage() { echo "Usage: $0 [-b(are)] [-d(aemon)] [-a(rgs) \"<args>\"]" 1>&2; exit 0; }

while getopts ":bda:" __opts; do
    case "${__opts}" in
        b)
            export _APP_BARE=True
            ;;
        d)
            export _APP_DAEMON=True
            ;;
        a)
            export _APP_ARGS=${OPTARG}
            ;;
        h)
            usage
            ;;
        *)
            usage
            ;;
    esac
done

if [ -d ${__dir}/__envi ]
then
    . ${__dir}/__envi/bin/activate
    export PYTHONPATH=${__dir}/src
    if [ -z "${_APP_DAEMON}" ];
    then
        ${__dir}/__envi/bin/python -u ${PYTHONPATH}/navi/manual.py ${_APP_ARGS}
    else
        mkdir -p ${__dir}/__logs
        nohup ${__dir}/__envi/bin/python -u ${PYTHONPATH}/navi/manual.py ${_APP_ARGS} 0<&- &> ${__dir}/__logs/output.log &
    fi
else
    echo "Application not installed. Please run \`${__dir}/bin/install.sh\`"
    exit 1
fi