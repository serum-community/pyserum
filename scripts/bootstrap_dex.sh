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


if ! hash solana 2>/dev/null; then
    echo Installing Solana tool suite ...
    curl -sSf https://raw.githubusercontent.com/solana-labs/solana/v1.5.8/install/solana-install-init.sh | SOLANA_RELEASE=v1.5.8 sh -s - v1.5.8
    export PATH="/home/runner/.local/share/solana/install/active_release/bin:$PATH"
    if [ ! -f ~/.config/solana/id.json ]; then
        echo Generating keypair ...
        solana-keygen new -o ~/.config/solana/id.json --no-passphrase --silent
    fi
fi

solana-test-validator & echo $! > solana_test_validator.pid
solana config set --url "http://127.0.0.1:8899"
curl -s -L "https://github.com/serum-community/serum-dex/releases/download/v2/serum_dex-$os_type.so" > serum_dex.so
sleep 1
solana airdrop 10000
DEX_PROGRAM_ID="$(solana deploy --use-deprecated-loader serum_dex.so | jq .programId -r)"
echo DEX_PROGRAM_ID: "$DEX_PROGRAM_ID"
curl -s -L "https://github.com/serum-community/serum-dex/releases/download/v2/crank-$os_type" > crank
chmod +x crank
./crank l pyserum-setup ~/.config/solana/id.json "$DEX_PROGRAM_ID"

echo "dex_program_id: $DEX_PROGRAM_ID" >> crank.log
mv crank.log tests/crank.log
cat tests/crank.log
