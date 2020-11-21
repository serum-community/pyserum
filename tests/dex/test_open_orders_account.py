import base64

import pytest
from solana.publickey import PublicKey

from pyserum.dex.open_orders_account import OPEN_ORDERS_LAYOUT, OpenOrdersAccount
from tests.binary_file_path import OPEN_ORDER_ACCOUNT_BIN_PATH


# TODO: This tests is not ran due to the v1 layout to v2 layout upgrade, we
# should update the binary and make it work again
@pytest.mark.skip(reason="We need to upgrade to v2 layout.")
def test_decode_open_order_account_layout():
    """Test decode event queue."""
    with open(OPEN_ORDER_ACCOUNT_BIN_PATH, "r") as input_file:
        base64_res = input_file.read()
        data = base64.decodebytes(base64_res.encode("ascii"))
        open_order_account = OPEN_ORDERS_LAYOUT.parse(data)
        assert open_order_account.account_flags.open_orders
        assert open_order_account.account_flags.initialized
        assert PublicKey(open_order_account.market) == PublicKey("4r5Bw3HxmxAzPQ2ATUvgF2nFe3B6G1Z2Nq2Nwu77wWc2")
        assert PublicKey(open_order_account.owner) == PublicKey("7hJx7QMiVfjZSSADQ18oNKzqifJPMu18djYLkh4aYh5Q")
        # if there is no order the byte returned here will be all 0. In this case we have three orders.
        assert len([order for order in open_order_account.orders if int.from_bytes(order, "little") != 0]) == 3
        # the first three order are bid order
        assert int.from_bytes(open_order_account.is_bid_bits, "little") == 0b111


# TODO: This tests is not ran due to the v1 layout to v2 layout upgrade, we
# should update the binary and make it work again
@pytest.mark.skip(reason="We need to upgrade to v2 layout.")
def test_decode_open_order_account():
    """Test decode event queue."""
    with open(OPEN_ORDER_ACCOUNT_BIN_PATH, "r") as input_file:
        base64_res = input_file.read()
        data = base64.decodebytes(base64_res.encode("ascii"))
        open_order_account = OpenOrdersAccount.from_bytes(PublicKey(1), data)
        assert open_order_account.market == PublicKey("4r5Bw3HxmxAzPQ2ATUvgF2nFe3B6G1Z2Nq2Nwu77wWc2")
        assert open_order_account.owner == PublicKey("7hJx7QMiVfjZSSADQ18oNKzqifJPMu18djYLkh4aYh5Q")
        assert len([order for order in open_order_account.orders if order != 0]) == 3
        # the first three order are bid order
        assert open_order_account.is_bid_bits == 0b111
