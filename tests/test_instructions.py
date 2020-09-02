"""Test instructions."""

from solana.publickey import PublicKey

import src.instructions as inlib


def test_initialize_market():
    """Test initialize market."""
    params = inlib.InitializeMarketParams(
        market=PublicKey(0),
        request_queue=PublicKey(1),
        event_queue=PublicKey(3),
        bids=PublicKey(4),
        asks=PublicKey(5),
        base_vault=PublicKey(6),
        quote_vault=PublicKey(7),
        base_mint=PublicKey(8),
        quote_mint=PublicKey(9),
        base_lot_size=1,
        quote_lot_size=2,
        fee_rate_bps=3,
        vault_signer_nonce=4,
        quote_dust_threshold=5,
    )
    instruction = inlib.initialize_market(params)
    assert inlib.decode_initialize_market(instruction) == params
