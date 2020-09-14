#!/bin/bash

if [[ $KEEP_ARTIFACTS == "" ]]; then
    echo Deleting artifacts...
    rm -rf tests/crank.log crank serum_dex.so
fi
docker-compose down