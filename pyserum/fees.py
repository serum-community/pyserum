from solana.publickey import PublicKey
from pyserum.utils import get_layout_version

FEE_TIER_FEES = {
    # Base
    0: {"taker": 0.0022, "maker": -0.0003},
    # SRM2
    1: {"taker": 0.002, "maker": -0.0003},
    # SRM3
    2: {"taker": 0.0018, "maker": -0.0003},
    # SRM4
    3: {"taker": 0.0016, "maker": -0.0003},
    # SRM5
    4: {"taker": 0.0014, "maker": -0.0003},
    # SRM6
    5: {"taker": 0.0012, "maker": -0.0003},
    # MSRM
    6: {"taker": 0.001, "maker": -0.0005},
}


def supports_srm_fee_discount(program_id: PublicKey):
    return get_layout_version(program_id) > 1


def get_fee_rates(fee_tier: int):
    # use base fee on unknown
    return FEE_TIER_FEES.get(fee_tier, FEE_TIER_FEES.get(0))


def get_fee_tier(srm_balance=0, msrm_balance=0):
    fee_tier = 0
    if msrm_balance >= 1:
        fee_tier = 6
    elif srm_balance >= 1000000:
        fee_tier = 5
    elif srm_balance >= 100000:
        fee_tier = 4
    elif srm_balance >= 10000:
        fee_tier = 3
    elif srm_balance >= 1000:
        fee_tier = 2
    elif srm_balance >= 100:
        fee_tier = 1
    return fee_tier
