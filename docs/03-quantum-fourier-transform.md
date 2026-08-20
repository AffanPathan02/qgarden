# The Quantum Fourier Transform

## Definition

For an $n$-qubit register, the QFT maps a computational basis state
$|x\rangle$ to:

$$
\text{QFT}|x\rangle = \frac{1}{\sqrt{2^n}} \sum_{y=0}^{2^n-1} \exp\!\left(\frac{2\pi i \, x y}{2^n}\right) |y\rangle
$$

This is exactly the discrete Fourier transform applied to the amplitudes
of the state vector, implemented as a unitary circuit rather than a
classical $O(n \log n)$ FFT.

## Circuit construction (`src/qft.py`)

The circuit follows the standard recursive decomposition:

1. Apply a Hadamard to the top qubit.
2. Apply controlled-phase rotations $CP(\pi / 2^{n-\text{qubit}})$ from every qubit
   below it, each rotation half the angle of the previous.
3. Recurse on the remaining $n-1$ qubits.
4. Reverse the qubit order with SWAP gates, since the recursive
   construction produces the output in bit-reversed order relative to the
   input.

This gives an $O(n^2)$ gate count, an exponential improvement over the
classical FFT's $O(n \cdot 2^n)$ operations on a state vector of size $2^n$ —
though note this compares gate count to an *explicit* classical FFT over
all amplitudes; it does not mean an arbitrary "Fourier-related" classical
problem gets this speedup, only cases (like phase/period-finding) where a
quantum algorithm can act on superposed states directly and extract only a
small classical answer at the end.

## Verification

Rather than just asserting correctness, I checked the circuit's action
directly against the QFT's matrix definition:

```python
from qft import qft
import numpy as np
from qiskit.quantum_info import Operator

n = 3
op = Operator(qft(n)).data
N = 2**n
expected = np.array(
    [[np.exp(2j*np.pi*x*y/N) for y in range(N)] for x in range(N)]
) / np.sqrt(N)

assert np.allclose(op, expected, atol=1e-6)
```

This passes for $n = 3$ (and I re-ran it for $n = 4, 5$ while developing —
see `tests/test_qft.py`), confirming the H + controlled-phase + swap
construction really does implement the QFT matrix, not just "something
that looks plausible in a circuit diagram."

## Role in phase estimation

The **inverse** QFT (`inverse_qft_gate` in `src/qft.py`) is the second half
of quantum phase estimation, used in `src/shor.py`. Phase estimation
prepares a counting register whose amplitudes encode a phase $\varphi \approx k/r$ in
the Fourier basis; applying the inverse QFT converts that phase into a
(probabilistically) measurable computational-basis value, which classical
continued-fraction expansion then turns into the order `r`.
