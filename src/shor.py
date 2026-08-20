"""
Shor's algorithm for N = 15, following the standard order-finding structure:

  1. Quantum part (this module builds and runs the circuit):
     Prepare a counting register in superposition, apply controlled
     modular-exponentiation U^(2^k)|y> = |a^(2^k) * y mod N>, then apply the
     inverse QFT to the counting register and measure. This is quantum phase
     estimation applied to the eigenvalues of U, and yields (with high
     probability) a measurement s/2^n_count that is close to k/r, where r is
     the multiplicative order of a mod N.

  2. Classical part (continued fractions):
     Recover r from the measured phase via a continued-fraction expansion,
     then compute candidate factors as gcd(a^(r/2) - 1, N) and
     gcd(a^(r/2) + 1, N).

This mirrors the structure of the general algorithm; only the modular
exponentiation subroutine (modexp_mod15.py) is specialised to N = 15 to
keep the circuit small enough to simulate easily.
"""

from math import gcd
from fractions import Fraction

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from qft import inverse_qft_gate
from modexp_mod15 import controlled_amod15_power

N = 15


def build_shor_circuit(a: int, n_count: int = 8) -> QuantumCircuit:
    """Build the quantum phase estimation circuit for order-finding of a mod 15."""
    qc = QuantumCircuit(n_count + 4, n_count)

    for q in range(n_count):
        qc.h(q)

    qc.x(n_count)  # auxiliary register starts in state |1>

    for q in range(n_count):
        qc.append(controlled_amod15_power(a, q), [q] + list(range(n_count, n_count + 4)))

    qc.append(inverse_qft_gate(n_count), range(n_count))
    qc.measure(range(n_count), range(n_count))
    return qc


def run_once(a: int, n_count: int = 8, shots: int = 1, seed: int = None) -> dict:
    qc = build_shor_circuit(a, n_count)
    backend = AerSimulator()
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots, seed_simulator=seed)
    return job.result().get_counts()


def phase_to_order(measured_bits: str, n_count: int) -> int:
    """Turn a measured bitstring into a candidate order r via continued fractions."""
    decimal = int(measured_bits, 2)
    phase = decimal / (2 ** n_count)
    frac = Fraction(phase).limit_denominator(N)
    return frac.denominator


def find_factors(a: int, n_count: int = 8, shots: int = 20, seed: int = 42):
    """Run the circuit multiple times and try to extract non-trivial factors of 15."""
    counts = run_once(a, n_count=n_count, shots=shots, seed=seed)
    attempts = []

    for bitstring, freq in sorted(counts.items(), key=lambda kv: -kv[1]):
        r = phase_to_order(bitstring, n_count)
        attempts.append({"measured": bitstring, "count": freq, "candidate_r": r})

        if r % 2 != 0:
            continue
        x = pow(a, r // 2, N)
        if x == N - 1:
            continue
        f1, f2 = gcd(x - 1, N), gcd(x + 1, N)
        if f1 not in (1, N) or f2 not in (1, N):
            return {"a": a, "order_r": r, "factors": sorted({f1, f2} - {1, N}), "attempts": attempts}

    return {"a": a, "order_r": None, "factors": [], "attempts": attempts}


if __name__ == "__main__":
    for a in (7, 2, 8, 11, 13):
        result = find_factors(a)
        print(f"a={a:2d} -> order candidates tried: "
              f"{[att['candidate_r'] for att in result['attempts'][:5]]} "
              f"| factors found: {result['factors']}")
