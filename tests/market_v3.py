from solana.rpc.api import Client
from pyserum.market import Market
from solana.publickey import PublicKey
from conf.keys import mykey

http_client = Client("https://deeptrading.rpcpool.com/4dd4ef2c8f1b0a798cddd7874225")
stubbed_market_pk = PublicKey("teE55QrL4a4QSfydR9dnHF97jgCfptpuigbb53Lo95g")
stubbed_dex_program_pk = PublicKey("9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin")
market = Market.load(http_client, stubbed_market_pk, stubbed_dex_program_pk, force_use_request_queue=True)



## 读行情

asks = market.load_asks()
# Show all current ask order
print("Ask Orders:")
for ask in asks:
    print("Order id: %d, price: %f, size: %f." % (
          ask.order_id, ask.info.price, ask.info.size))

print("\n")
# # Show all current bid order
# print("Bid Orders:")
# bids = market.load_bids()
# for bid in bids:
#     print(f"Order id: {bid.order_id}, price: {bid.info.price}, size: {bid.info.size}.")
#

## my order

my_orders = market.find_open_orders_accounts_for_owner(mykey.public_key)
print(my_orders)