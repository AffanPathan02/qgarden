# Quantum Gates — Prerequisite Reference

This is a reference for readers who want the gate-level vocabulary before
reading `docs/01` through `docs/05`. Every gate below is one used
somewhere in this repository's code — the "Used in this repo" line under
each gate points to exactly where.

If you're comfortable with complex numbers and matrix multiplication but
new to quantum computing, read this top to bottom once; after that it's
meant to be a lookup table.

---

## 0. Notation recap

A single qubit's state is a vector $\alpha|0\rangle + \beta|1\rangle$
with $|\alpha|^2+|\beta|^2=1$, where

$$
|0\rangle = \begin{pmatrix}1\\0\end{pmatrix}, \qquad
|1\rangle = \begin{pmatrix}0\\1\end{pmatrix}
$$

A gate is a matrix; applying a gate to a state is matrix–vector
multiplication. A gate on $n$ qubits is a $2^n \times 2^n$ **unitary**
matrix ($U^\dagger U = I$) — every gate is invertible, and its inverse is
also a valid gate (just its conjugate transpose).

For multi-qubit gates below, matrices are written in the ordering Qiskit
uses (little-endian: qubit 0 is the rightmost bit of the basis label).

---

## 1. Single-qubit gates

### Pauli-X (NOT)

$$
X = \begin{pmatrix}0 & 1\\1 & 0\end{pmatrix}
$$

Flips $|0\rangle \leftrightarrow |1\rangle$ — the quantum analogue of a
classical NOT gate, but unitary/reversible rather than merely a boolean
function.

**Used in this repo:** `src/modexp_mod15.py` (`U.x(q)` remaps residues
mod 15), `src/grover.py` (`phase_oracle` and `diffuser` both use blocks of
X gates to remap the marked/zero states onto the all-ones string before a
multi-controlled-Z).

### Pauli-Y and Pauli-Z

$$
Y = \begin{pmatrix}0 & -i\\i & 0\end{pmatrix}, \qquad
Z = \begin{pmatrix}1 & 0\\0 & -1\end{pmatrix}
$$

$Z$ leaves $|0\rangle$ unchanged and flips the *phase* of $|1\rangle$
(multiplies it by $-1$) — it doesn't change measurement probabilities in
the computational basis, only relative phase. $Y = iXZ$, combining both
effects.

**Used in this repo:** `Z` (and its multi-controlled generalization)
implements the phase-flip oracle in `src/grover.py::phase_oracle` and the
diffuser's "invert about the mean" step — Grover's algorithm works
entirely by manipulating phases, not by ever measuring mid-circuit.

### Hadamard (H)

$$
H = \frac{1}{\sqrt{2}}\begin{pmatrix}1 & 1\\1 & -1\end{pmatrix}
$$

Maps $|0\rangle \to \frac{1}{\sqrt2}(|0\rangle+|1\rangle)$ and
$|1\rangle \to \frac{1}{\sqrt2}(|0\rangle-|1\rangle)$ — creates equal
superposition from a definite state. $H^2 = I$, so applying it twice
undoes it.

**Used in this repo:** starts every algorithm here. `src/qft.py::qft_rotations`
applies it at each recursive level; `src/shor.py` uses it to put the
counting register into superposition before phase estimation;
`src/grover.py` uses it both to prepare $|s\rangle$ initially and inside
the diffuser.

### Phase gate family: S, T, and general $P(\theta)$

$$
P(\theta) = \begin{pmatrix}1 & 0\\0 & e^{i\theta}\end{pmatrix}, \qquad
S = P(\pi/2), \qquad T = P(\pi/4)
$$

Leaves $|0\rangle$ untouched, multiplies $|1\rangle$'s amplitude by
$e^{i\theta}$. $S$ and $T$ are the $\theta=\pi/2$ and $\theta=\pi/4$
special cases, common enough to have their own names (and their own
efficient hardware implementations on real devices).

**Used in this repo:** the *controlled* version of $P(\theta)$, not the
single-qubit gate directly — see CP below, the actual workhorse of the
QFT.

### Rotation gates $R_x, R_y, R_z$

$$
R_z(\theta) = \begin{pmatrix}e^{-i\theta/2} & 0\\0 & e^{i\theta/2}\end{pmatrix},
\qquad
R_x(\theta) = \begin{pmatrix}\cos\frac\theta2 & -i\sin\frac\theta2\\-i\sin\frac\theta2 & \cos\frac\theta2\end{pmatrix},
\qquad
R_y(\theta) = \begin{pmatrix}\cos\frac\theta2 & -\sin\frac\theta2\\\sin\frac\theta2 & \cos\frac\theta2\end{pmatrix}
$$

Rotations by angle $\theta$ about the $x$, $y$, $z$ axes of the Bloch
sphere (the geometric picture of a single qubit's state space). $P(\theta)$
above is $R_z(\theta)$ up to an overall (unmeasurable) global phase.

**Used in this repo:** not called directly by name, but conceptually this
is *why* `docs/05-grovers-algorithm.md`'s "rotation by $2\theta$" picture
works — a Grover iteration acting within a 2D real subspace is exactly a
rotation, the same underlying idea as $R_y(\theta)$ acting on a single
qubit's Bloch sphere, just in a higher-dimensional subspace spanned by
$|\text{good}\rangle$ and $|\text{bad}\rangle$ instead of $|0\rangle$ and
$|1\rangle$.

### Identity ($I$)

$$
I = \begin{pmatrix}1 & 0\\0 & 1\end{pmatrix}
$$

Does nothing. Included here because it shows up implicitly in derivations
(e.g. the diffuser is defined as $2|s\rangle\langle s| - I$ in
`docs/05-grovers-algorithm.md`).

---

## 2. Multi-qubit gates

### CNOT (controlled-X)

$$
\text{CNOT} = \begin{pmatrix}
1&0&0&0\\
0&1&0&0\\
0&0&0&1\\
0&0&1&0
\end{pmatrix}
$$

Flips the target qubit if and only if the control qubit is $|1\rangle$.
The basic building block for entangling two qubits — applying CNOT to
$H|0\rangle \otimes |0\rangle$ produces the Bell state
$|\Phi^+\rangle$ discussed in `docs/02-entanglement-measurement.md`.

**Used in this repo:** as the general pattern "controlled-$U$" — see
below; a controlled-$X$ specifically doesn't appear standalone in this
repo's code, but every controlled gate used here (`mcx`, controlled
modular multiplication, controlled-phase) is a direct generalization of
this idea.

### Controlled-Phase (CP)

$$
CP(\theta) = \begin{pmatrix}
1&0&0&0\\
0&1&0&0\\
0&0&1&0\\
0&0&0&e^{i\theta}
\end{pmatrix}
$$

Applies a phase $e^{i\theta}$ to the target **only when both qubits are
$|1\rangle$** — unlike CNOT, this gate is symmetric in control/target (it
doesn't matter which qubit you call "control").

**Used in this repo:** the core gate of the QFT. `src/qft.py::qft_rotations`
builds the entire QFT from Hadamards and a cascade of `circuit.cp(angle,
qubit, n)` calls, each rotation half the angle of the last — this is
literally where the "Fourier" structure of the QFT comes from.

### Controlled-U (general)

For any single-qubit (or multi-qubit) unitary $U$, the controlled version
acts as $U$ on the target register when the control qubit is $|1\rangle$,
and identity otherwise:

$$
CU = |0\rangle\langle0| \otimes I \; + \; |1\rangle\langle1| \otimes U
$$

**Used in this repo:** this is the general pattern behind
`src/modexp_mod15.py::controlled_amod15_power`, which builds
controlled-$U_a^{2^k}$ for the modular-multiplication unitary $U_a$ —
the central subroutine of Shor's algorithm's phase estimation circuit
(`docs/04-shors-algorithm.md`, §3.2). Qiskit's `.control(1)` method
(used in that file) constructs this automatically from a given circuit.

### SWAP

$$
\text{SWAP} = \begin{pmatrix}
1&0&0&0\\
0&0&1&0\\
0&1&0&0\\
0&0&0&1
\end{pmatrix}
$$

Exchanges the states of two qubits.

**Used in this repo:** `src/qft.py::swap_registers` reverses qubit order
at the end of the QFT circuit (the recursive H+CP construction produces
output in bit-reversed order — SWAPs fix this). Also appears inside
`src/modexp_mod15.py::_c_amod15`, where — specifically for $N=15$ —
"multiply by $a$ mod 15" reduces to a permutation of 4-qubit basis states
implementable directly as a handful of SWAPs and X gates, rather than
needing a general arithmetic circuit.

### Toffoli / multi-controlled-X (CCX, MCX)

$$
\text{Toffoli} = \begin{pmatrix}
I_6 & 0\\
0 & X
\end{pmatrix}
\quad\text{(6×6 identity block, then X on the last two-dimensional block)}
$$

Flips the target qubit iff **both** (or, for MCX, **all**) control qubits
are $|1\rangle$. The Toffoli gate is universal for classical reversible
computation and, combined with $H$, is universal for quantum computation.

**Used in this repo:** `src/grover.py` builds both the oracle
(`phase_oracle`) and the diffuser using a multi-controlled-Z, itself built
from `qc.h(n-1)`, `qc.mcx(...)`, `qc.h(n-1)` — the standard trick that a
controlled-$Z$ on the last qubit sandwiched between Hadamards is
equivalent to a controlled-$X$ (MCX), since $HXH = Z$.

---

## 3. How these compose into the algorithms in this repo

| Algorithm | Gate sequence, in words |
|---|---|
| **QFT** (`src/qft.py`) | $H$ + cascading $CP(\theta)$ at shrinking angles, then SWAPs to reverse order. |
| **Shor's algorithm** (`src/shor.py`) | $H^{\otimes n}$ for superposition → controlled-$U_a^{2^k}$ (built from SWAP/X per `modexp_mod15.py`) for phase kickback → inverse QFT → measurement. |
| **Grover's algorithm** (`src/grover.py`) | $H^{\otimes n}$ for superposition → repeat[ phase oracle (X + MCX/MCZ + X) → diffuser (H + X + MCX/MCZ + X + H) ] → measurement. |

If a gate above is unfamiliar when you hit it in `docs/03`, `docs/04`, or
`docs/05`, this file is the place to come back to.

## 4. Further reading

- Nielsen & Chuang, *Quantum Computation and Quantum Information*, ch. 4
  (the standard reference for this entire gate set).
- Qiskit gate reference: https://docs.quantum.ibm.com/api/qiskit/circuit-library
