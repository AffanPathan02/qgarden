"""
Controlled modular multiplication / exponentiation, specialised to N = 15.

Full modular exponentiation is expensive to build as a generic reversible
circuit. For teaching and small-scale demonstration purposes, N = 15 is the
standard case: it is small enough that "multiply by a, mod 15" can be
written directly as a fixed permutation of the 4-qubit computational basis
states {0,...,14} (state 15 is simply unused), implemented with SWAP and X
gates rather than a general arithmetic circuit.

This module implements controlled-U for U|y> = |a*y mod 15>, for every a
coprime to 15 (a in {2,4,7,8,11,13,14}), and repeated-squaring to build
controlled-U^(2^power).
"""

from qiskit import QuantumCircuit
from qiskit.circuit import Gate


def _c_amod15(a: int) -> QuantumCircuit:
    """Controlled multiplication-by-a mod 15 as a 4-target-qubit permutation.

    Built as an explicit permutation circuit on the 4-qubit register
    (representing residues 0-15, states >14 unused/never reached), controlled
    by one extra control qubit.
    """
    if a not in (2, 4, 7, 8, 11, 13, 14):
        raise ValueError("a must be coprime with 15 and in {2,4,7,8,11,13,14}")

    U = QuantumCircuit(4, name=f"{a} mod 15")

    if a in (2, 13):
        U.swap(2, 3)
        U.swap(1, 2)
        U.swap(0, 1)
    if a in (7, 8):
        U.swap(0, 1)
        U.swap(1, 2)
        U.swap(2, 3)
    if a in (4, 11):
        U.swap(1, 3)
        U.swap(0, 2)
    if a in (7, 11, 13):
        for q in range(4):
            U.x(q)

    return U


def controlled_amod15_power(a: int, power: int) -> Gate:
    """Return controlled-U^(2^power) where U|y> = |a*y mod 15>."""
    U = _c_amod15(a)
    U_power = U.repeat(2 ** power)
    U_power.name = f"{a}^{2**power} mod 15"
    gate = U_power.to_gate()
    gate = gate.control(1)
    return gate
