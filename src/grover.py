"""
Grover's algorithm: amplitude amplification for unstructured search.

Given a boolean oracle f: {0,1}^n -> {0,1} that marks a set of "good"
states (implemented as a phase-flip oracle), Grover's algorithm finds a
marked state in O(sqrt(2^n / M)) queries, where M is the number of marked
states — a quadratic speedup over the O(2^n / M) queries a classical
algorithm needs to search an unstructured list.
"""

import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def phase_oracle(marked_states: list[str], n: int) -> QuantumCircuit:
    """Build a phase-flip oracle: |x> -> -|x> for each marked bitstring, else |x> -> |x>.

    Implemented via a multi-controlled Z, using X gates to remap each
    marked bitstring onto the all-ones string before/after the MCZ.
    """
    qc = QuantumCircuit(n, name="Oracle")
    for state in marked_states:
        if len(state) != n:
            raise ValueError(f"marked state {state!r} must have length {n}")
        zero_positions = [i for i, bit in enumerate(reversed(state)) if bit == "0"]

        for q in zero_positions:
            qc.x(q)

        if n == 1:
            qc.z(0)
        else:
            qc.h(n - 1)
            qc.mcx(list(range(n - 1)), n - 1)
            qc.h(n - 1)

        for q in zero_positions:
            qc.x(q)

    return qc


def diffuser(n: int) -> QuantumCircuit:
    """Grover diffuser: inversion about the mean, i.e. reflection about |s>=H^n|0>."""
    qc = QuantumCircuit(n, name="Diffuser")
    qc.h(range(n))
    qc.x(range(n))

    if n == 1:
        qc.z(0)
    else:
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)

    qc.x(range(n))
    qc.h(range(n))
    return qc


def optimal_iterations(n: int, num_marked: int) -> int:
    """Nearest integer to (pi/4) * sqrt(2^n / M), the optimal Grover iteration count."""
    N = 2 ** n
    return max(1, round((math.pi / 4) * math.sqrt(N / num_marked)))


def grover_circuit(marked_states: list[str], n: int, iterations: int | None = None) -> QuantumCircuit:
    if iterations is None:
        iterations = optimal_iterations(n, len(marked_states))

    qc = QuantumCircuit(n, n)
    qc.h(range(n))  # uniform superposition |s>

    oracle = phase_oracle(marked_states, n).to_gate()
    diff = diffuser(n).to_gate()

    for _ in range(iterations):
        qc.append(oracle, range(n))
        qc.append(diff, range(n))

    qc.measure(range(n), range(n))
    return qc


def run_grover(marked_states: list[str], n: int, iterations: int | None = None, shots: int = 1000, seed: int = 42) -> dict:
    qc = grover_circuit(marked_states, n, iterations)
    backend = AerSimulator()
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots, seed_simulator=seed)
    counts = job.result().get_counts()
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


if __name__ == "__main__":
    n = 4
    for marked in (["1011"], ["0110"], ["0000", "1111"]):
        it = optimal_iterations(n, len(marked))
        counts = run_grover(marked, n, iterations=it, shots=2000)
        top = list(counts.items())[: len(marked) + 1]
        hit_rate = sum(c for s, c in counts.items() if s in marked) / sum(counts.values())
        print(f"marked={marked} iterations={it} top_counts={top} "
              f"hit_rate={hit_rate:.3f}")
