import base64
from types import SimpleNamespace

from src.market import MARKET_LAYOUT, Market, Order, OrderBook

MARKET_DATA_HEX = "736572756d030000000000000054f23cbc4d93795ce75ecd8173bcf436923112f7b6b024f3afd9b6789124b9680000000000000000c73690f1d4b87aa9337848369c20a682b37e8dcb33f4237a2a8f8b0abd64bd1cd9c75c9a58645ff02ab0741cd6d1790067957d2266165b767259b358ded270fb2dbc6d44f2ab58dce432b5bb31d98517366d6e24e69c0bf5b926ead9ec658935408ffd71c50000000000000000000000e1a461a046199877c4cd3cbafc61c3dfdb088e737b7193a3d28e72b709421fc4544fec927c000000a4fc4c12000000006400000000000000f422ea23ada9e1a9d100ba8443deb041c231e0f79ee6d07d1c1f7042fe4a1ade3b236ea4ba636227dfa22773f41fa02cc91842c2e9330e2ac0a987dc68b520e8c58676b5751c48e22c3bcc6edda8f75f76b1596b9874bd5714366e32d84e3bc0400501895361982c4be67d03af519ac7fd96a8a79f5b15ec7af79f6b70290bf740420f00000000001027000000000000000000000000000070616464696e67"  # noqa: E501 # pylint: disable=line-too-long
DATA = bytes.fromhex(MARKET_DATA_HEX)

MARKET_ENCODE = SimpleNamespace(
    **{
        "account_flags": SimpleNamespace(
            **{
                "initialized": True,
                "market": True,
                "bids": False,
            }
        ),
        "vault_signer_nonce": 0,
        "base_fees_accrued": 0,
        "quote_dust_threshold": 100,
        "base_lot_size": 100,
        "quote_lot_size": 10,
        "fee_rate_bps": 0,
    }
)

BTC_USDC_MARKET = Market(MARKET_ENCODE, 6, 6, None, "https://api.mainnet-beta.solana.com/")


def test_parse_market_state():
    parsed_market = MARKET_LAYOUT.parse(DATA)
    assert parsed_market.account_flags.initialized
    assert parsed_market.account_flags.market
    assert not parsed_market.account_flags.open_orders
    assert parsed_market.vault_signer_nonce == 0
    assert parsed_market.base_fees_accrued == 0
    assert parsed_market.quote_dust_threshold == 100
    assert parsed_market.fee_rate_bps == 0


def test_order_book_iterator():
    """Test order book parsing."""
    with open("tests/binary/ask_order_binary.txt", "r") as input_file:
        base64_res = input_file.read()
        data = base64.decodebytes(base64_res.encode("ascii"))
        order_book = OrderBook.decode(BTC_USDC_MARKET, data)
        total_orders = sum([1 for _ in order_book.orders()])
        assert total_orders == 15


def test_order_book_get_l2():
    with open("tests/binary/ask_order_binary.txt", "r") as input_file:
        base64_res = input_file.read()
        data = base64.decodebytes(base64_res.encode("ascii"))
        order_book = OrderBook.decode(BTC_USDC_MARKET, data)
        for i in range(1, 16):
            assert i == len(order_book.get_l2(i))
        assert [(11744.6, 4.0632, 117446, 40632)] == order_book.get_l2(1)


def test_order_book_iterable():
    with open("tests/binary/ask_order_binary.txt", "r") as input_file:
        base64_res = input_file.read()
        data = base64.decodebytes(base64_res.encode("ascii"))
        order_book = OrderBook.decode(BTC_USDC_MARKET, data)
        cnt = 0
        for order in order_book:
            cnt += 1
            assert isinstance(order, Order)
        assert cnt == 15
