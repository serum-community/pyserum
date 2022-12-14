

from pyserum.connection import conn
from pyserum.market import Market

from solana.publickey import PublicKey


def get_orderbook_sync():
    cc = conn("https://api.mainnet-beta.solana.com/")
    market_address = "8BnEgHoWFysVcuFFX7QztDmzuH8r5ZFvyP3sYwn1XTh6"  # Openbook SOL/USDC

    # Load the given DEX
    market = Market.load(cc, PublicKey(market_address))

    # Show all current bid orders
    print("Bid Orders:")
    bids = market.load_bids()
    for bid in bids:
        print(f"Order id: {bid.order_id}, price: {bid.info.price}, size: {bid.info.size}.")

    print("\n")

    # Show all current ask orders
    asks = market.load_asks()
    print("Ask Orders:")
    for ask in asks:
        print("Order id: %d, price: %f, size: %f." % (
              ask.order_id, ask.info.price, ask.info.size))



if __name__ == '__main__':

    get_orderbook_sync()



