"""Score hotspot (F4) — PUR. score = complexite x churn."""


def score(complexite: int, churn: int) -> float:
    return float(complexite * churn)
