[![Actions
Status](https://github.com/serum-community/pyserum/workflows/CI/badge.svg)](https://github.com/serum-community/pyserum/actions?query=workflow%3ACI)
[![Codecov](https://codecov.io/gh/serum-community/pyserum/branch/alpha/graph/badge.svg)](https://codecov.io/gh/serum-community/pyserum/branches/alpha)

# PySerum

Python client library for interacting with the [Project Serum](https://projectserum.com/) DEX.

## Get Started

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
          ask.order_id, ask.order_info.price, ask.order_info.size))

print("\n")
# Show all current bid order
print("Bid Orders:")
bids = market.load_bids()
for bid in bids:
    print("Order id: %d, price: %f, size: %f." % (
          bid.order_id, bid.order_info.price, bid.order_info.size))
```

### Market Addresses in Main Net

The source of truth of the market address can be found [here](https://github.com/project-serum/serum-js/blob/master/src/tokens_and_markets.ts). Feel free to open a PR if the following addresses needs modification or addition.

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
