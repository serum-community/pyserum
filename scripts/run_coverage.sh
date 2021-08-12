#!/bin/bash

pipenv run pytest -m  "not integration and not async_integration" --cov=./ --cov-report=xml --cov-append

bash scripts/bootstrap_dex.sh

wait_time=20
echo "Waiting $wait_time seconds to make sure the market has started"
sleep $wait_time


pipenv run pytest -m integration --cov=./ --cov-report=xml --cov-append

bash scripts/clean_up.sh

bash scripts/bootstrap_dex.sh

wait_time=20
echo "Waiting $wait_time seconds to make sure the market has started"
sleep $wait_time

exit_code=1
if (pipenv run pytest -m async_integration --cov=./ --cov-report=xml --cov-append); then
  echo "The script ran ok"
  exit_code=0
fi

bash scripts/clean_up.sh

exit $exit_code
