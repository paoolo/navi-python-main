#!/bin/bash

export ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export NAVI_DIR=${ROOT_DIR}/src/navi
export COMMON_DIR=${NAVI_DIR}/proto

set -x

protoc -I ${COMMON_DIR} --python_out=${COMMON_DIR} ${COMMON_DIR}/controlmsg.proto