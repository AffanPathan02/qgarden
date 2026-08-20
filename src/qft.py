"""
Quantum Fourier Transform (QFT) building blocks.

The QFT maps computational basis states to the Fourier basis:

    QFT |x> = (1/sqrt(2^n)) * sum_y  exp(2*pi*i*x*y / 2^n) |y>

It is built from Hadamard gates and controlled phase-rotation gates
(CP), followed by a qubit-order reversal (implemented with SWAPs).
"""

from qiskit import QuantumCircuit
from qiskit.circuit import Gate


def qft_rotations(circuit: QuantumCircuit, n: int) -> QuantumCircuit:
    """Apply the H + controlled-phase rotation cascade to the first n qubits.

    Recursive structure: put qubit n-1 (top of the remaining register) into
    superposition, then apply a chain of controlled phase rotations from
    every qubit below it, each rotation smaller by a factor of two. Recurse
    on the remaining n-1 qubits.
    """
    if n == 0:
        return circuit
    n -= 1
    circuit.h(n)
    for qubit in range(n):
        angle = 3.14159265358979 / (2 ** (n - qubit))
        circuit.cp(angle, qubit, n)
    qft_rotations(circuit, n)
    return circuit


def swap_registers(circuit: QuantumCircuit, n: int) -> QuantumCircuit:
    """Reverse qubit order so the output matches the standard QFT convention."""
    for qubit in range(n // 2):
        circuit.swap(qubit, n - qubit - 1)
    return circuit


def qft(n: int) -> QuantumCircuit:
    """Build an n-qubit QFT circuit."""
    circuit = QuantumCircuit(n, name=f"QFT_{n}")
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    return circuit


def inverse_qft(n: int) -> QuantumCircuit:
    """Build the inverse QFT by inverting the forward circuit."""
    qc = qft(n)
    inv = qc.inverse()
    inv.name = f"QFT_{n}†"
    return inv


def qft_gate(n: int) -> Gate:
    return qft(n).to_gate()


def inverse_qft_gate(n: int) -> Gate:
    return inverse_qft(n).to_gate()
