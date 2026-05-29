import math
from decimal import Decimal, ROUND_HALF_UP

RISK_FREE_RATE = 0.065  # default 6.5% (configurable)


def check_put_call_parity(
    call_price: float,
    put_price: float,
    spot: float,
    strike: float,
    expiry_days: int,
    threshold: float = 0.02,
    rate: float = RISK_FREE_RATE,
) -> dict:
    """
    Check put-call parity: C - P = S - K * e^(-rT)
    Returns a dict with violation flag and deviation magnitude.
    """
    if expiry_days <= 0:
        return {"violation": False, "deviation": 0.0, "reason": "expired"}

    T = expiry_days / 365.0
    theoretical_diff = spot - strike * math.exp(-rate * T)
    actual_diff = call_price - put_price

    # Use Decimal for precision
    deviation = abs(
        Decimal(str(actual_diff)) - Decimal(str(theoretical_diff))
    ) / Decimal(str(spot))
    deviation = float(deviation.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))

    violation = deviation > threshold
    return {
        "violation": violation,
        "deviation": deviation,
        "theoretical_diff": round(theoretical_diff, 4),
        "actual_diff": round(actual_diff, 4),
        "threshold": threshold,
    }