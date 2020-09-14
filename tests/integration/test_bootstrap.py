import pytest
from solana.account import Account
from solana.publickey import PublicKey


@pytest.mark.integration
def test_payer(stubbed_payer):
    assert isinstance(stubbed_payer, Account)


@pytest.mark.integration
def test_base_mint(stubbed_base_mint):
    assert isinstance(stubbed_base_mint, Account)


@pytest.mark.integration
def test_base_wallet(stubbed_base_wallet):
    assert isinstance(stubbed_base_wallet, Account)


@pytest.mark.integration
def test_base_vault_pk(stubbed_base_vault_pk):
    assert isinstance(stubbed_base_vault_pk, PublicKey)


@pytest.mark.integration
def test_quote_mint(stubbed_quote_mint):
    assert isinstance(stubbed_quote_mint, Account)


@pytest.mark.integration
def test_quote_wallet(stubbed_quote_wallet):
    assert isinstance(stubbed_quote_wallet, Account)


@pytest.mark.integration
def test_quote_vault_pk(stubbed_quote_vault_pk):
    assert isinstance(stubbed_quote_vault_pk, PublicKey)


@pytest.mark.integration
def test_market_pk(stubbed_market_pk):
    assert isinstance(stubbed_market_pk, PublicKey)


@pytest.mark.integration
def test_event_q_pk(stubbed_event_q_pk):
    assert isinstance(stubbed_event_q_pk, PublicKey)


@pytest.mark.integration
def test_req_q_pk(stubbed_req_q_pk):
    assert isinstance(stubbed_req_q_pk, PublicKey)


@pytest.mark.integration
def test_bids_pk(stubbed_bids_pk):
    assert isinstance(stubbed_bids_pk, PublicKey)


@pytest.mark.integration
def test_asks_pk(stubbed_asks_pk):
    assert isinstance(stubbed_asks_pk, PublicKey)


@pytest.mark.integration
def test_bid_account_pk(stubbed_bid_account_pk):
    assert isinstance(stubbed_bid_account_pk, PublicKey)


@pytest.mark.integration
def test_ask_account_pk(stubbed_ask_account_pk):
    assert isinstance(stubbed_ask_account_pk, PublicKey)


@pytest.mark.integration
def test_dex_program_pk(stubbed_dex_program_pk):
    assert isinstance(stubbed_dex_program_pk, PublicKey)
