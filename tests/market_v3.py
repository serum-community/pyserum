from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.types import TxOpts

from conf.keys import mykey, rpc_api
from pyserum.enums import OrderType, Side
from pyserum.market import Market

# constant
SYMBOL = "RAY-USDT"
SPL_USDT = PublicKey("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB")
SPL_RAY = PublicKey("4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R")
SPL_Token_Program = PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SPL_Associated_Token_Account_Program = PublicKey("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
stubbed_base_wallet, _ = mykey.public_key.find_program_address(
    seeds=[bytes(mykey.public_key), bytes(SPL_Token_Program), bytes(SPL_RAY)],
    program_id=SPL_Associated_Token_Account_Program,
)
stubbed_quote_wallet, _ = mykey.public_key.find_program_address(
    seeds=[bytes(mykey.public_key), bytes(SPL_Token_Program), bytes(SPL_USDT)],
    program_id=SPL_Associated_Token_Account_Program,
)


# create market
def create_market():
    http_client = Client(rpc_api)
    stubbed_market_pk = PublicKey("teE55QrL4a4QSfydR9dnHF97jgCfptpuigbb53Lo95g")
    stubbed_dex_program_pk = PublicKey("9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin")
    market = Market.load(http_client, stubbed_market_pk, stubbed_dex_program_pk, force_use_request_queue=False)
    return market


def load_asks_and_bids(market):
    # load asks and bids
    asks = market.load_asks()
    bids = market.load_bids()
    for ask in asks:
        print(f"Ask Order id: {ask.order_id}, price: {ask.info.price}, size: {ask.info.size}.")
    for bid in bids:
        print(f"Bid Order id: {bid.order_id}, price: {bid.info.price}, size: {bid.info.size}.")


def load_my_order(market: Market, own_address: PublicKey):
    res = market.find_open_orders_accounts_for_owner(mykey.public_key)
    print(f"find_open_orders_accounts_for_owner: {res}, {own_address}")


def load_queue(market):
    event_queue = market.load_event_queue()
    request_queue = market.load_request_queue()
    print(f"event_queue: {event_queue}")
    print(f"request_queue: {request_queue}")


def place_order(market: Market):
    res = market.place_order(
        payer=stubbed_quote_wallet,
        owner=mykey,
        side=Side.BUY,
        order_type=OrderType.IOC,
        limit_price=4,
        max_quantity=0.2,
        opts=TxOpts(skip_confirmation=False),
    )
    print(f"place_order: {res}")


def match_order(market: Market):
    res = market.match_orders(
        fee_payer=mykey,
        limit=2,
        opts=TxOpts(skip_confirmation=False),
    )
    print(f"match_orders: {res}")


def settle_fund(market: Market):
    open_order_accounts = market.find_open_orders_accounts_for_owner(owner_address=mykey.public_key)
    for open_order_account in open_order_accounts:
        print(f"open_order_account: {open_order_account.__dict__}")
    res = market.settle_funds(
        owner=mykey,
        open_orders=open_order_accounts[0],
        base_wallet=stubbed_base_wallet,
        quote_wallet=stubbed_quote_wallet,
    )
    print(f"settle_funds: {res}")


def cancel_order(market: Market):
    orders = market.load_orders_for_owner(owner_address=mykey.public_key)
    for order in orders:
        print(f"order: {order}")
    res = market.cancel_order(
        owner=mykey,
        order=orders[0],
        opts=TxOpts(skip_confirmation=False),
    )
    print(f"cancel_order: {res}")


def load_fills(market: Market):
    res = market.load_fills(10)
    print(f"load_fills: {res}")


if __name__ == "__main__":
    m = create_market()
    # load_asks_and_bids(m)
    # load_my_order(m, mykey.public_key)
    # load_queue(m)
    place_order(m)
    # match_order(m)
    # settle_fund(m)
    # cancel_order(m)
    # load_fills(m)
