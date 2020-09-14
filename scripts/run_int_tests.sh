#!/bin/bash

bash scripts/run_serum_in_docker.sh

wait_time=20
echo "Waiting $wait_time seconds to make sure the market has started"
sleep $wait_time



exit_code=1
if (pipenv run pytest -vv -m integration); then
  echo "The script ran ok"
  exit_code=0
fi

bash scripts/clean_up.sh

exit $exit_code
