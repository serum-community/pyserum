import pytest
from solana.account import Account

from .crank import genesis
from .utils import assert_valid_response


@pytest.mark.integration
def test_create_accounts_and_send_transaction(stubbed_payer):
    mint_account = Account()
    resp = genesis(stubbed_payer, mint_account, 6)
    assert_valid_response(resp)
