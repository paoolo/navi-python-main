#!/bin/bash

export __dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export __dir="$( dirname ${__dir} )"

usage() { echo "Usage: $0 [-d(aemon)] [-p(rofile)] [-a(rgs) \"<args>\"]" 1>&2; exit 0; }

while getopts ":dpa:" __opts; do
    case "${__opts}" in
        d)
            export _APP_DAEMON=True
            ;;
        p)
            export _APP_PROFILE=True
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

    if [ -z "${_APP_PROFILE}" ];
    then
        if [ -z "${_APP_DAEMON}" ];
        then
            ${__dir}/__envi/bin/python -u ${PYTHONPATH}/navi/main.py ${_APP_ARGS}
        else
            mkdir -p ${__dir}/__logs
            command -v nohup > /dev/null 2>&1 || { echo "Need to have 'nohup' installed!" >&2; exit 1; }
            nohup ${__dir}/__envi/bin/python -u ${PYTHONPATH}/navi/main.py ${_APP_ARGS} 0<&- &> ${__dir}/__logs/output.log &
        fi
    else
        export _APP_TEMP=$(mktemp -d)

        ${__dir}/__envi/bin/python -u -m cProfile -o ${_APP_TEMP}/output.pstats ${PYTHONPATH}/navi/main.py ${_APP_ARGS}

        ${__dir}/__envi/bin/gprof2dot -f pstats --output ${_APP_TEMP}/output.dot ${_APP_TEMP}/output.pstats
        command -v nohup > /dev/null 2>&1 || { echo "Need to have 'dot' installed!" >&2; exit 1; }
        dot -Tpng ${_APP_TEMP}/output.dot -o ${__dir}/profile-main-$(date +"%Y%m%d-%H%M%S").png

        rm -rf ${_APP_TEMP}
    fi
else
    echo "Application not installed. Please run \`${__dir}/bin/install.sh\`"
    exit 1
fi