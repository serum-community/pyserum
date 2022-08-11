from typing import Tuple, Union

from solana.publickey import PublicKey

MSRM_MINT = PublicKey("MSRMcoVyrFxnSgo5uXwone5SKcGhT1KEJMFEkMEWf9L")
SRM_MINT = PublicKey("SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt")
MSRM_DECIMALS = 0
SRM_DECIMALS = 6


def get_fee_rates(fee_tier: int) -> Tuple[float, float]:  # taker, maker
    taker, maker = 0.0022, -0.0003
    if fee_tier == 1:  # SRM2
        taker, maker = 0.002, -0.0003
    elif fee_tier == 2:  # SRM3
        taker, maker = 0.0018, -0.0003
    elif fee_tier == 3:  # SRM4
        taker, maker = 0.0016, -0.0003
    elif fee_tier == 4:  # SRM5
        taker, maker = 0.0014, -0.0003
    elif fee_tier == 5:  # SRM6
        taker, maker = 0.0012, -0.0003
    elif fee_tier == 6:  # MSRM
        taker, maker = 0.001, -0.0005
    return taker, maker


def get_fee_tier(msrm_balance: Union[int, float], srm_balance: Union[int, float]) -> int:
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
