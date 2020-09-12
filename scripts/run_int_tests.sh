if [ ! -d "serum-dex" ]; then
    git clone https://github.com/serum-community/serum-dex.git
fi

cd serum-dex
docker-compose up -d
./do.sh build dex
solana airdrop 10000
DEX_PROGRAM_ID="$(solana deploy --use-deprecated-loader dex/target/bpfel-unknown-unknown/release/serum_dex.so | jq .programId -r)"
echo DEX_PROGRAM_ID: $DEX_PROGRAM_ID
cd crank
cargo run -- l pyserum-setup ~/.config/solana/id.json $DEX_PROGRAM_ID
echo "dex_program_id: $DEX_PROGRAM_ID" >> crank.log
cp crank.log ../../tests
cd ../..
cat tests/crank.log
