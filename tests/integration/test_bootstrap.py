import pytest
from solana.publickey import PublicKey


@pytest.mark.integration
def test_serum_dex(serum_dex, wallet):
    """Make sure serum_dex fixture is populated with public keys."""
    assert isinstance(serum_dex["coin_mint"], PublicKey)
    assert isinstance(serum_dex["pc_mint"], PublicKey)
    assert isinstance(serum_dex["market"], PublicKey)
    assert isinstance(serum_dex["req_q"], PublicKey)
    assert isinstance(serum_dex["event_q"], PublicKey)
    assert isinstance(serum_dex["bids"], PublicKey)
    assert isinstance(serum_dex["asks"], PublicKey)
    assert isinstance(serum_dex["coin_vault"], PublicKey)
    assert isinstance(serum_dex["pc_vault"], PublicKey)
    assert isinstance(serum_dex["vault_signer_key"], PublicKey)
    assert isinstance(serum_dex["wallet"], PublicKey)
    assert isinstance(serum_dex["bid_account"], PublicKey)
    assert isinstance(serum_dex["ask_account"], PublicKey)
    assert isinstance(serum_dex["dex_program_id"], PublicKey)
    assert serum_dex["wallet"] == str(wallet.public_key())
