import base64

import pytest
from construct import Container
from solana.rpc.api import Client

from src.instructions import DEFAULT_DEX_PROGRAM_ID
from src.market import Market, OrderBook, State
from src.market.types import AccountFlags, Order, OrderInfo

from .binary_file_path import ASK_ORDER_BIN_PATH


@pytest.fixture(scope="module")
def stubbed_data() -> bytes:
    MARKET_DATA_HEX = (  # pylint: disable=invalid-name
        "736572756d030000000000000054f23cbc4d93795ce75ecd8173bcf436923112f7b6b024f3afd9b6789124b9680000000000"
        "000000c73690f1d4b87aa9337848369c20a682b37e8dcb33f4237a2a8f8b0abd64bd1cd9c75c9a58645ff02ab0741cd6d179"
        "0067957d2266165b767259b358ded270fb2dbc6d44f2ab58dce432b5bb31d98517366d6e24e69c0bf5b926ead9ec65893540"
        "8ffd71c50000000000000000000000e1a461a046199877c4cd3cbafc61c3dfdb088e737b7193a3d28e72b709421fc4544fec"
        "927c000000a4fc4c12000000006400000000000000f422ea23ada9e1a9d100ba8443deb041c231e0f79ee6d07d1c1f7042fe"
        "4a1ade3b236ea4ba636227dfa22773f41fa02cc91842c2e9330e2ac0a987dc68b520e8c58676b5751c48e22c3bcc6edda8f7"
        "5f76b1596b9874bd5714366e32d84e3bc0400501895361982c4be67d03af519ac7fd96a8a79f5b15ec7af79f6b70290bf740"
        "420f00000000001027000000000000000000000000000070616464696e67"
    )
    return bytes.fromhex(MARKET_DATA_HEX)


@pytest.fixture(scope="module")
def stubbed_market() -> Market:
    conn = Client("http://stubbed_endpoint:123/")
    market_state = State(
        Container(
            dict(
                account_flags=AccountFlags(
                    initialized=True,
                    market=True,
                    bids=False,
                ),
                quote_dust_threshold=100,
                base_lot_size=100,
                quote_lot_size=10,
            )
        ),
        program_id=DEFAULT_DEX_PROGRAM_ID,
        base_mint_decimals=6,
        quote_mint_decimals=6,
    )
    return Market(conn, market_state)


def test_parse_market_state(stubbed_data):  # pylint: disable=redefined-outer-name
    parsed_market = State.LAYOUT().parse(stubbed_data)
    assert parsed_market.account_flags.initialized
    assert parsed_market.account_flags.market
    assert not parsed_market.account_flags.open_orders
    assert parsed_market.vault_signer_nonce == 0
    assert parsed_market.base_fees_accrued == 0
    assert parsed_market.quote_dust_threshold == 100
    assert parsed_market.fee_rate_bps == 0


def test_order_book_iterator(stubbed_market):  # pylint: disable=redefined-outer-name
    """Test order book parsing."""
    with open(ASK_ORDER_BIN_PATH, "r") as input_file:
        base64_res = input_file.read()
        data = base64.decodebytes(base64_res.encode("ascii"))
        order_book = OrderBook.decode(stubbed_market, data)
        total_orders = sum([1 for _ in order_book.orders()])
        assert total_orders == 15


def test_order_book_get_l2(stubbed_market):  # pylint: disable=redefined-outer-name
    with open(ASK_ORDER_BIN_PATH, "r") as input_file:
        base64_res = input_file.read()
        data = base64.decodebytes(base64_res.encode("ascii"))
        order_book = OrderBook.decode(stubbed_market, data)
        for i in range(1, 16):
            assert i == len(order_book.get_l2(i))
        assert [OrderInfo(11744.6, 4.0632, 117446, 40632)] == order_book.get_l2(1)


def test_order_book_iterable(stubbed_market):  # pylint: disable=redefined-outer-name
    with open(ASK_ORDER_BIN_PATH, "r") as input_file:
        base64_res = input_file.read()
        data = base64.decodebytes(base64_res.encode("ascii"))
        order_book = OrderBook.decode(stubbed_market, data)
        cnt = 0
        for order in order_book:
            cnt += 1
            assert isinstance(order, Order)
        assert cnt == 15
