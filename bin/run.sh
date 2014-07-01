#!/bin/bash

export __dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export __dir="$( dirname ${__dir} )"

usage() { echo "Usage: $0 [-m(anual)] [-b(are)] [-d(aemon)] [-p(rofile)] [-a(rgs) \"<args>\"]" 1>&2; exit 0; }

while getopts ":mbdpa:" __opts; do
    case "${__opts}" in
        m)
            export _APP_MANUAL=True
            ;;
        b)
            export _APP_BARE=True
            ;;
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

if [ -z "${_APP_MANUAL}" ];
then
    export _APP_PATH=auto
else
    export _APP_PATH=manual
fi

if [ -d ${__dir}/__envi ]
then
    . ${__dir}/__envi/bin/activate
    export PYTHONPATH=${__dir}/src

    if [ -z "${_APP_PROFILE}" ];
    then
        if [ -z "${_APP_DAEMON}" ];
        then
            ${__dir}/__envi/bin/python -u ${PYTHONPATH}/navi/${_APP_PATH}.py ${_APP_ARGS}
        else
            mkdir -p ${__dir}/__logs
            # TODO(paoolo) check if `nohup` exists?
            /usr/bin/nohup ${__dir}/__envi/bin/python -u ${PYTHONPATH}/navi/${_APP_PATH}.py ${_APP_ARGS} 0<&- &> ${__dir}/__logs/output.log &
        fi
    else
        export _APP_TEMP=$(mktemp -d)

        ${__dir}/__envi/bin/python -u -m cProfile -o ${_APP_TEMP}/output.pstats ${PYTHONPATH}/navi/${_APP_PATH}.py ${_APP_ARGS}

        ${__dir}/__envi/bin/gprof2dot -f pstats --output ${_APP_TEMP}/output.dot ${_APP_TEMP}/output.pstats
        # TODO(paoolo) check if `dot` exists?
        /usr/bin/dot -Tpng ${_APP_TEMP}/output.dot -o ${__dir}/profile-${_APP_PATH}-$(date +"%Y%m%d-%H%M%S").png

        rm -rf ${_APP_TEMP}
    fi
else
    echo "Application not installed. Please run \`${__dir}/bin/install.sh\`"
    exit 1
fi