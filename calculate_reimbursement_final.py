#!/usr/bin/env python3
"""Top Coder Challenge — ACME Legacy Reimbursement replica (v3)

Changelog — 2025‑06‑07 (“sigmoid gate” release)
------------------------------------------------
* **Dynamic receipt weight** — A logistic *gate* scales the receipt
  coefficient and long‑trip penalty based on
  `R = receipts / miles`:

      gate(R) = 1 / (1 + exp(-0.7·(R – 5)))

  • When receipts are lavish for the mileage (R ≫ 5) → gate ≈ 1
    (behaves like v2).
  • When receipts look ordinary (R ≈ 2–3) → gate ≈ 0.1–0.2, sharply
    reducing the impact of receipts and the long‑trip penalty.
* **Long‑trip penalty still −$85 per extra day** but multiplied by *gate*.
* Base linear coefficients unchanged.

Empirical impact
~~~~~~~~~~~~~~~~
* Fixes the new high‑error set (cases 684 / 152 / 548 / 711 / 996) to < $200
  absolute error.
* Keeps all previously‑fixed luxury 1‑to‑2‑day outliers within ±$100.

Formula
~~~~~~~
    gate = 1 / (1 + e^{−0.7·( R − 5 )})
    base = 116.3323·days  +  0.45118·miles  – 268.9806
    base += 0.52597·gate·receipts
    if days > 7:
        base −= 85·gate·(days − 7)
    return round(base, 2)

Usage
~~~~~
    ./legacy_reimbursement_solver.py <days> <miles> <receipts>
Prints the reimbursement to **stdout** rounded to two decimals.
"""
import math
import sys
from typing import Tuple

# —— Base linear model coefficients (from original OLS fit) ——
A_DAYS      = 116.3323007   # $ per travel day
B_MILES     =   0.45118319  # $ per mile travelled
C_RECEIPTS  =   0.52596549  # reimbursed share of receipts (before gating)
D_INTERCEPT = -268.98059207 # base offset

# —— Long‑trip parameters ——
LONG_TRIP_THRESHOLD_DAYS   = 7      # penalise from day 8 onward
LONG_TRIP_PENALTY_PER_DAY  = 85.0   # $ per extra day

# —— Gate parameters ——
CENTER_R   = 5.0   # R where gate ≈ 0.5
SLOPE      = 0.7   # logistic slope
EPS_MILES  = 1.0   # avoid div‑by‑zero when miles ≈ 0


def _gate(receipts: float, miles: float) -> float:
    """Logistic gate ∈ (0,1] based on receipts‑to‑mile ratio."""
    r = receipts / max(miles, EPS_MILES)
    return 1.0 / (1.0 + math.exp(-SLOPE * (r - CENTER_R)))


def predict(days: float, miles: float, receipts: float) -> float:
    """Return reimbursement rounded to 2 decimals using v3 rules."""
    g = _gate(receipts, miles)

    amt = (
        A_DAYS * days +
        B_MILES * miles +
        D_INTERCEPT +
        C_RECEIPTS * g * receipts
    )

    # Long‑trip penalty scales with the same gate
    if days > LONG_TRIP_THRESHOLD_DAYS:
        amt -= LONG_TRIP_PENALTY_PER_DAY * g * (days - LONG_TRIP_THRESHOLD_DAYS)

    return round(amt + 1e-9, 2)  # half‑up cent rounding


def _parse_args(argv: list[str]) -> Tuple[float, float, float]:
    if len(argv) != 4:
        raise SystemExit("Usage: legacy_reimbursement_solver.py <days> <miles> <receipts>")
    try:
        days     = float(argv[1])
        miles    = float(argv[2])
        receipts = float(argv[3])
    except ValueError as exc:
        raise SystemExit(f"Invalid numeric input: {exc}") from None
    return days, miles, receipts


if __name__ == "__main__":
    d, m, r = _parse_args(sys.argv)
    print(f"{predict(d, m, r):.2f}")
