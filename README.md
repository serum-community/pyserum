[![Actions
Status](https://github.com/serum-community/pyserum/workflows/CI/badge.svg)](https://github.com/serum-community/pyserum/actions?query=workflow%3ACI)
[![Codecov](https://codecov.io/gh/serum-community/pyserum/branch/alpha/graph/badge.svg)](https://codecov.io/gh/serum-community/pyserum/branches/alpha)

# PySerum

Python client library for interacting with the [Project Serum](https://projectserum.com/) DEX.

## Get Started

```python
from pyserum.market import Market

endpoint = "https://api.mainnet-beta.solana.com/"
market_address = "CAgAeMD7quTdnr6RPa7JySQpjf3irAmefYNdTb6anemq" # Address for BTC/USDC

# Load the given market
market = Market.load(endpoint, market_address, None)
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

The source of truth of the market address can be found [here](https://github.com/project-serum/serum-js/blob/master/pyserum/tokens_and_markets.ts). Feel free to open a PR if the following addresses needs modification or addition.

| Currency Pair |                   Address                    |
| :-----------: | :------------------------------------------: |
|   MSRM/USDT   | H4snTKK9adiU15gP22ErfZYtro3aqR9BTMXiH3AwiUTQ |
|   MSRM/USDC   | 7kgkDyW7dmyMeP8KFXzbcUZz1R2WHsovDZ7n3ihZuNDS |
|   BTC/USDT    | 8AcVjMG2LTbpkjNoyq8RwysokqZunkjy3d5JDzxC6BJa |
|   BTC/USDC    | CAgAeMD7quTdnr6RPa7JySQpjf3irAmefYNdTb6anemq |
|   ETH/USDT    | HfCZdJ1wfsWKfYP2qyWdXTT5PWAGWFctzFjLH48U1Hsd |
|   ETH/USDC    | ASKiV944nKg1W9vsf7hf3fTsjawK6DwLwrnB2LH9n61c |
|   SRM/USDT    | HARFLhSq8nECZk4DVFKvzqXMNMA9a3hjvridGMFizeLa |
|   SRM/USDC    | 68J6nkWToik6oM9rTatKSR5ibVSykAtzftBUEAvpRsys |
|   FTT/USDT    | DHDdghmkBhEpReno3tbzBPtsxCt6P3KrMzZvxavTktJt |
|   FTT/USDC    | FZqrBXz7ADGsmDf1TM9YgysPUfvtG8rJiNUrqDpHc9Au |
|   YFI/USDT    | 5zu5bTZZvqESAAgFsr12CUMxdQvMrvU9CgvC1GW8vJdf |
|   YFI/USDC    | FJg9FUtbN3fg3YFbMCFiZKjGh5Bn4gtzxZmtxFzmz9kT |
|   LINK/USDT   | F5xschQBMpu1gD2q1babYEAVJHR1buj1YazLiXyQNqSW |
|   LINK/USDC   | 7GZ59DMgJ7D6dfoJTpszPayTRyua9jwcaGJXaRMMF1my |

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
