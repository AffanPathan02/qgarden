# The Quantum Circuit Model

## Qubits and state space

A single qubit's state is a unit vector in a 2-dimensional complex Hilbert
space, written in Dirac (bra-ket) notation as

$$
|\psi\rangle = \alpha|0\rangle + \beta|1\rangle, \qquad |\alpha|^2 + |\beta|^2 = 1
$$

An $n$-qubit register lives in the tensor-product space $(\mathbb{C}^2)^{\otimes n}$,
of dimension $2^n$. This exponential scaling of the state space with the
number of qubits is the resource that quantum algorithms exploit — and the
reason classical simulation of quantum circuits becomes intractable beyond
a few dozen qubits.

## Gates as unitary operators

Quantum gates are unitary operators $U$ (satisfying $U^\dagger U = I$)
acting on this state space. Because they're unitary, every gate is
reversible — there's no quantum analogue of an irreversible classical gate
like AND. Some gates used throughout this repository:

- **Hadamard (H):** maps $|0\rangle$ to the equal superposition
  $\frac{1}{\sqrt{2}}(|0\rangle+|1\rangle)$. Used to put registers into
  superposition, e.g. at the start of phase estimation in `src/qft.py`.
- **Controlled-Phase (CP):** applies a phase $e^{i\theta}$ to $|1\rangle$
  conditional on a control qubit being $|1\rangle$. The QFT is built almost entirely from H
  and CP gates (`src/qft.py::qft_rotations`).
- **CNOT / controlled-U:** applies `X` (or a general unitary `U`) to a
  target qubit conditional on a control qubit. `src/modexp_mod15.py` builds
  a controlled modular-multiplication unitary this way.
- **SWAP:** exchanges the states of two qubits; used both inside the QFT
  (to correct qubit ordering) and inside the mod-15 multiplication circuit
  (which happens to reduce, for N=15, to permutations built from swaps and
  X gates).

## Measurement

Measurement in the computational basis collapses a superposition
probabilistically: measuring $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$
yields $0$ with probability $|\alpha|^2$ and $1$ with probability
$|\beta|^2$. This is why quantum
algorithms are typically run many times (see `shots` in `src/shor.py`) —
individual runs sample from a distribution, and the algorithm's job is to
shape that distribution so the *useful* answer is heavily favored.

## Circuits as composition

A circuit is a sequence of gates applied to a register, which is exactly
composition of unitary operators — the full circuit's action is the matrix
product of its gates (in reverse order of application). This repository
verifies that composition explicitly: `docs/03-quantum-fourier-transform.md`
checks the built QFT circuit's unitary matrix against the closed-form QFT
definition.

## Further reading

- Nielsen & Chuang, *Quantum Computation and Quantum Information*, ch. 4.
- Qiskit documentation: https://docs.quantum.ibm.com/
