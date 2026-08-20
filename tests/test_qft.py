"""
Verifies the QFT circuit implementation against the closed-form QFT matrix
definition, and checks Shor's algorithm correctly factors 15.

Run with: python -m pytest tests/ -v   (from repo root)
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qft import qft
from qiskit.quantum_info import Operator
from shor import find_factors
from grover import run_grover, optimal_iterations
import math


def dft_matrix(n: int) -> np.ndarray:
    N = 2 ** n
    return np.array(
        [[np.exp(2j * np.pi * x * y / N) for y in range(N)] for x in range(N)]
    ) / np.sqrt(N)


def test_qft_matches_dft_definition():
    for n in (2, 3, 4):
        op = Operator(qft(n)).data
        expected = dft_matrix(n)
        assert np.allclose(op, expected, atol=1e-6), f"QFT circuit mismatch for n={n}"


def test_shor_factors_15():
    for a in (2, 7, 8, 11, 13):
        result = find_factors(a)
        assert set(result["factors"]) == {3, 5}, f"Expected factors {{3,5}} for a={a}, got {result['factors']}"


def test_grover_matches_theoretical_success_probability():
    n, marked = 4, ["1011"]
    N = 2 ** n
    theta = math.asin(math.sqrt(len(marked) / N))
    k = optimal_iterations(n, len(marked))
    theoretical_p = math.sin((2 * k + 1) * theta) ** 2

    counts = run_grover(marked, n, iterations=k, shots=4000)
    empirical_p = sum(c for s, c in counts.items() if s in marked) / sum(counts.values())

    assert abs(empirical_p - theoretical_p) < 0.03, (
        f"Empirical hit rate {empirical_p:.3f} deviates from theory {theoretical_p:.3f}"
    )


if __name__ == "__main__":
    test_qft_matches_dft_definition()
    print("QFT matrix test passed.")
    test_shor_factors_15()
    print("Shor factoring test passed.")
    test_grover_matches_theoretical_success_probability()
    print("Grover success-probability test passed.")
