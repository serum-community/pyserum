[![Actions
Status](https://github.com/serum-community/pyserum/workflows/CI/badge.svg)](https://github.com/serum-community/pyserum/actions?query=workflow%3ACI)
[![Codecov](https://codecov.io/gh/serum-community/pyserum/branch/alpha/graph/badge.svg)](https://codecov.io/gh/serum-community/pyserum/branches/alpha)

# PySerum

Python client library for interacting with the [Project Serum](https://projectserum.com/) DEX.

## Install

```sh
pip install pyserum
```

## Getting Started

### Mainnet Market Addresses

```python
from pyserum.connection import get_live_markets, get_token_mints
print("tokens: ")
print(get_token_mints())
print("markets: ")
print(get_live_markets())
```

The source of truth of the market addresses can be found
[here](https://github.com/project-serum/serum-js/blob/master/src/markets.json).

### Get Orderbook

```python
from pyserum.connection import conn
from pyserum.market import Market

cc = conn("https://api.mainnet-beta.solana.com/")
market_address = "5LgJphS6D5zXwUVPU7eCryDBkyta3AidrJ5vjNU6BcGW" # Address for BTC/USDC

# Load the given market
market = Market.load(cc, market_address)
asks = market.load_asks()
# Show all current ask order
print("Ask Orders:")
for ask in asks:
    print("Order id: %d, price: %f, size: %f." % (
          ask.order_id, ask.info.price, ask.info.size))

print("\n")
# Show all current bid order
print("Bid Orders:")
bids = market.load_bids()
for bid in bids:
    print(f"Order id: {bid.order_id}, price: {bid.info.price}, size: {bid.info.size}.")
```

### Get Orderbook (Async)

```python
import asyncio
from pyserum.async_connection import async_conn
from pyserum.market import AsyncMarket


async def main():
    market_address = "5LgJphS6D5zXwUVPU7eCryDBkyta3AidrJ5vjNU6BcGW"  # Address for BTC/USDC
    async with async_conn("https://api.mainnet-beta.solana.com/") as cc:
        # Load the given market
        market = await AsyncMarket.load(cc, market_address)
        asks = await market.load_asks()
        # Show all current ask order
        print("Ask Orders:")
        for ask in asks:
            print(f"Order id: {ask.order_id}, price: {ask.info.price}, size: {ask.info.size}.")
        print("\n")
        # Show all current bid order
        print("Bid Orders:")
        bids = await market.load_bids()
        for bid in bids:
            print(f"Order id: {bid.order_id}, price: {bid.info.price}, size: {bid.info.size}.")


asyncio.run(main())

```

### Support

Need help? You can find us on the Serum Discord:

[![Discord Chat](https://img.shields.io/discord/739225212658122886?color=blueviolet)](https://discord.gg/fvbaQ6uyv5)

## Development

### Setup

1. Install pipenv.

```sh
brew install pipenv
```

2. Install dev dependencies.

```sh
pipenv install --dev
```

3. Activate the pipenv shell.

```sh
pipenv shell
```

### Format

```
make format
```

### Lint

```sh
make lint
```

### Tests

```sh
# Unit tests
make unit-tests
# Integration tests
make int-tests
```

### Using Jupyter Notebook

```sh
make notebook
```

### Start Serum in Docker image

```bash
./scripts/bootstrap_dex.sh
```

This will start a docker container with `solana` image and deploy a serum DEX which you can use for testing.

The market address, program id, and wallet addresses can be found in the new `crank.log` file after the script runs successfully.
