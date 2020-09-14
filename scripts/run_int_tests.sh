#!/bin/bash

bash scripts/run_serum_in_docker.sh

wait_time=10
echo "Waiting $wait_time seconds to make sure the market has started"
sleep $wait_time

pipenv run pytest -vv -m integration

bash scripts/clean_up.sh