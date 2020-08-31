from typing import Dict

from construct import BitsInteger, BitsSwapped, BitStruct, Flag  # type: ignore

_EMPTY_FLAG = ""

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
        _EMPTY_FLAG / BitsInteger(57),
    )
)


def decode_account_flags(raw_flags: bytes) -> Dict:
    return _ACCOUNT_FLAGS_LAYOUT.parse(raw_flags)


def encode_account_flags(flag_params: Dict) -> bytes:
    flag_params[None] = False  # Set empty flag
    return _ACCOUNT_FLAGS_LAYOUT.build(flag_params)
