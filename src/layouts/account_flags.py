from typing import Dict

from construct import BitStruct, BitsSwapped, Flag  # type: ignore

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
        _EMPTY_FLAG / Flag,  # XXX: I can't get Padding to work correctly. # pylint: disable=fixme
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
        _EMPTY_FLAG / Flag,
    )
)


def decode_account_flags(raw_flags: bytes) -> Dict:
    return _ACCOUNT_FLAGS_LAYOUT.parse(raw_flags)


def encode_account_flags(flag_params: Dict) -> bytes:
    flag_params[None] = False  # XXX: To take care of empty flags?  pylint: disable=fixme
    return _ACCOUNT_FLAGS_LAYOUT.build(flag_params)
