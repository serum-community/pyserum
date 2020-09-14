#!/bin/bash

set -e

os_type=""

if [[ $OSTYPE == "linux-gnu"* ]]; then
    os_type="linux"
elif [[ $OSTYPE == "darwin"* ]]; then
    os_type="darwin"
else
    echo $OSTYPE is not supported
    exit 1
fi

if [ ! -d "serum-dex" ]; then
    git clone https://github.com/serum-community/serum-dex.git
fi

cd serum-dex
docker-compose up -d
solana config set --url "http://localhost:8899"
curl -s -L "https://github.com/serum-community/serum-dex/releases/download/refs%2Fheads%2Fmaster/serum_dex-$os_type.so" > serum_dex.so
solana airdrop 10000
DEX_PROGRAM_ID="$(solana deploy --use-deprecated-loader serum_dex.so | jq .programId -r)"
echo DEX_PROGRAM_ID: $DEX_PROGRAM_ID
cd crank
cargo run -- l pyserum-setup ~/.config/solana/id.json $DEX_PROGRAM_ID
echo "dex_program_id: $DEX_PROGRAM_ID" >> crank.log
cp crank.log ../../tests
cd ../..
cat tests/crank.log
pipenv run pytest -vv -m integration
rm -rf tests/crank.log
docker kill serum-dex_localnet_1
