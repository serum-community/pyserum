#!/bin/bash

set -e

os_type=""

if [[ $OSTYPE == "linux-gnu"* ]]; then
    os_type="linux"
elif [[ $OSTYPE == "darwin"* ]]; then
    os_type="darwin"
else
    echo "$OSTYPE is not supported."
    exit 1
fi

docker-compose up -d
solana config set --url "http://localhost:8899"
curl -s -L "https://github.com/serum-community/serum-dex/releases/download/refs%2Fheads%2Fmaster/serum_dex-$os_type.so" > serum_dex.so
sleep 1
solana airdrop 10000
DEX_PROGRAM_ID="$(solana deploy --use-deprecated-loader serum_dex.so | jq .programId -r)"
echo DEX_PROGRAM_ID: $DEX_PROGRAM_ID
curl -s -L "https://github.com/serum-community/serum-dex/releases/download/refs%2Fheads%2Fmaster/crank-$os_type" > crank
chmod +x crank
./crank l pyserum-setup ~/.config/solana/id.json $DEX_PROGRAM_ID
echo "dex_program_id: $DEX_PROGRAM_ID" >> crank.log
mv crank.log tests/crank.log
cat tests/crank.log
pipenv run pytest -vv -m integration
if [[ $KEEP_ARTIFACTS == "" ]]; then
    echo Deleting artifacts...
    rm -rf tests/crank.log crank serum_dex.so
fi
docker-compose down
