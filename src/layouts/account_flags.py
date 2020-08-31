from typing import Dict

from construct import BitsInteger, BitStruct, BitsSwapped, Flag  # type: ignore

# We will use a bitstruct with 64 bits instead of the widebits implementation in serum-js.
_ACCOUNT_FLAGS_LAYOUT = BitsSwapped(  # Swap to little endian
    BitStruct(
        "initialized" / Flag,
        "market" / Flag,
        "openOrders" / Flag,
        "requestQueue" / Flag,
        "eventQueue" / Flag,
        "bids" / Flag,
        "asks" / Flag,
        BitsInteger(57),
    )
)


def decode_account_flags(raw_flags: bytes) -> Dict:
    """Parse account flags from bytes."""
    return _ACCOUNT_FLAGS_LAYOUT.parse(raw_flags)


def encode_account_flags(flag_params: Dict) -> bytes:
    """Serialize account flags to bytes."""
    flag_params[None] = False  # Set padding to false
    return _ACCOUNT_FLAGS_LAYOUT.build(flag_params)
