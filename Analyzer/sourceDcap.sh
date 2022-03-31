#!/bin/bash

export X509_USER_PROXY=/u/user/yeonjoon/proxy.cert
export LD_PRELOAD="/usr/lib64/libpdcap.so"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/lib64/dcap"

python ./haddhisto.py