from solana.publickey import PublicKey
from pyserum.utils import get_layout_version


def supports_srm_fee_discount(program_id: PublicKey):
    return get_layout_version(program_id) > 1


def get_fee_rates(fee_tier: int):
    if fee_tier == 1:
        # SRM2
        return {"taker": 0.002, "maker": -0.0003}
    if fee_tier == 2:
        # SRM3
        return {"taker": 0.0018, "maker": -0.0003}
    if fee_tier == 3:
        # SRM4
        return {"taker": 0.0016, "maker": -0.0003}
    if fee_tier == 4:
        # SRM5
        return {"taker": 0.0014, "maker": -0.0003}
    if fee_tier == 5:
        # SRM6
        return {"taker": 0.0012, "maker": -0.0003}
    if fee_tier == 6:
        # MSRM
        return {"taker": 0.001, "maker": -0.0005}
    # base
    return {"taker": 0.0022, "maker": -0.0003}


def get_fee_tier(srm_balance=0, msrm_balance=0):
    if msrm_balance >= 1:
        return 6
    if srm_balance >= 1000000:
        return 5
    if srm_balance >= 100000:
        return 4
    if srm_balance >= 10000:
        return 3
    if srm_balance >= 1000:
        return 2
    if srm_balance >= 100:
        return 1
    return 0
