# Quantum Computing: Notes & Implementations

Independent study repository covering the theoretical foundations of
quantum computing and a from-scratch, verified implementation of Shor's
algorithm. Built while self-studying quantum information theory alongside
professional software engineering work.

## Contents

| | |
|---|---|
| [`docs/01-circuit-model.md`](docs/01-circuit-model.md) | Qubits, gates as unitary operators, measurement |
| [`docs/02-entanglement-measurement.md`](docs/02-entanglement-measurement.md) | Entanglement and its role in phase estimation |
| [`docs/03-quantum-fourier-transform.md`](docs/03-quantum-fourier-transform.md) | QFT construction, with a matrix-level correctness check |
| [`docs/04-shors-algorithm.md`](docs/04-shors-algorithm.md) | Order-finding, the full algorithm, and RSA implications |
| [`src/qft.py`](src/qft.py) | QFT / inverse QFT circuit construction |
| [`src/modexp_mod15.py`](src/modexp_mod15.py) | Controlled modular exponentiation, specialised to N=15 |
| [`src/shor.py`](src/shor.py) | Phase estimation circuit + classical continued-fraction post-processing |
| [`tests/test_qft.py`](tests/test_qft.py) | Verifies the QFT against its matrix definition and confirms 15 = 3×5 is recovered |

## Quickstart

```bash
pip install -r requirements.txt
cd src && python shor.py
```

Expected output — every valid choice of `a` recovers the correct factors
of 15:

```
a= 7 -> order candidates tried: [1, 4] | factors found: [3, 5]
a= 2 -> order candidates tried: [1, 4] | factors found: [3, 5]
a= 8 -> order candidates tried: [1, 4] | factors found: [3, 5]
a=11 -> order candidates tried: [2]    | factors found: [3, 5]
a=13 -> order candidates tried: [1, 4] | factors found: [3, 5]
```

Run the test suite:

```bash
python -m pytest tests/ -v
```

## Scope

This is a small, fully-simulated, N=15 instance of Shor's algorithm —
chosen because it's the largest case where the modular-exponentiation
subroutine can be written as an explicit qubit permutation and the whole
circuit stays easy to simulate and to reason about by hand. The goal was
depth over scale: understanding and verifying every stage of the
algorithm (superposition → controlled modular exponentiation → inverse
QFT → measurement → classical continued-fraction post-processing), not
building a circuit that scales to cryptographically relevant N. See
`docs/04-shors-algorithm.md` for what would need to change for a general
N.

## Roadmap

- [ ] Grover's algorithm (amplitude amplification) write-up + implementation
- [ ] General (non-hardcoded) modular exponentiation for arbitrary N
- [ ] Quantum key distribution (BB84) notes
- [ ] Notes on quantum error correction basics

## Background

Written while independently studying the mathematical foundations of
quantum computing (Dirac notation, Hilbert spaces, the Schrödinger
equation) alongside 3+ years of professional software engineering
experience.
