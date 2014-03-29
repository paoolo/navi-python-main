#!/bin/bash

protoc -I=./ --python_out=./ ./controlmsg.proto