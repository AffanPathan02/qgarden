# Grover's Algorithm

## 1. The problem

Given an unstructured search space of size $N = 2^n$ and a boolean oracle
$f : \{0,1\}^n \to \{0,1\}$ marking $M$ "good" states, find a marked state.
Classically, with no structure to exploit, this requires $O(N/M)$ queries
on average. Grover's algorithm finds a marked state using only
$O(\sqrt{N/M})$ oracle queries — a quadratic, not exponential, speedup, but
provably optimal: no quantum algorithm can do better than
$\Omega(\sqrt{N/M})$ queries for black-box search.

## 2. The geometric picture

Let $|s\rangle = H^{\otimes n}|0\rangle^{\otimes n} = \frac{1}{\sqrt{N}}\sum_{x=0}^{N-1} |x\rangle$
be the uniform superposition. Split the computational basis into "good"
(marked) and "bad" (unmarked) states, and define the normalized
superpositions over each:

$$
|\text{good}\rangle = \frac{1}{\sqrt{M}} \sum_{x \,:\, f(x)=1} |x\rangle,
\qquad
|\text{bad}\rangle = \frac{1}{\sqrt{N-M}} \sum_{x \,:\, f(x)=0} |x\rangle
$$

Then $|s\rangle$ lives entirely in the 2-dimensional real subspace spanned
by $|\text{good}\rangle$ and $|\text{bad}\rangle$:

$$
|s\rangle = \sin\theta \,|\text{good}\rangle + \cos\theta \,|\text{bad}\rangle,
\qquad
\theta = \arcsin\sqrt{\frac{M}{N}}
$$

Grover's algorithm works entirely within this 2D subspace — this is what
makes the geometric ("rotation") picture exact, not an approximation.

### The oracle as a reflection

The phase oracle $O$ ($O|x\rangle = -|x\rangle$ if $x$ is marked, else
$|x\rangle$) acts as a reflection about $|\text{bad}\rangle$ in this plane:

$$
O = I - 2|\text{good}\rangle\langle\text{good}|
$$

### The diffuser as a reflection

The diffuser $D = 2|s\rangle\langle s| - I$ (inversion about the mean —
`diffuser()` in `src/grover.py`, built as $H^{\otimes n}(2|0\rangle\langle
0| - I)H^{\otimes n}$) reflects about $|s\rangle$.

### One Grover iteration is a rotation

The composition $G = D \cdot O$ of two reflections in a 2D plane is a
**rotation** by angle $2\theta$ toward $|\text{good}\rangle$. Applying $G$
repeatedly rotates the state vector from its initial angle $\theta$ (above
$|\text{bad}\rangle$) toward $|\text{good}\rangle$:

$$
G^k |s\rangle = \sin\big((2k+1)\theta\big)\,|\text{good}\rangle
              + \cos\big((2k+1)\theta\big)\,|\text{bad}\rangle
$$

so the probability of measuring a marked state after $k$ iterations is

$$
P(k) = \sin^2\big((2k+1)\theta\big)
$$

## 3. Choosing the number of iterations

$P(k)$ is maximized (closest to 1) when $(2k+1)\theta \approx \pi/2$, i.e.

$$
k^{*} = \left\lfloor \frac{\pi}{4\theta} \right\rceil
       \approx \left\lfloor \frac{\pi}{4}\sqrt{\frac{N}{M}} \right\rceil
$$

(the small-angle approximation $\theta \approx \sqrt{M/N}$ holds well when
$M \ll N$). This is exactly `optimal_iterations()` in `src/grover.py`.
**Overshooting matters**: applying more than $k^*$ iterations keeps
rotating *past* $|\text{good}\rangle$ and the success probability falls
again — Grover's algorithm is not "more iterations is always better."

## 4. Verifying this repo's implementation against the closed form

Rather than just trusting the simulator's output, I checked the empirical
hit rate against the exact formula above (`tests/test_qft.py::test_grover_matches_theoretical_success_probability`):

For $n=4$ ($N=16$), one marked state ($M=1$): $\theta = \arcsin(1/4)$,
optimal $k^{*}=3$, giving

$$
P(3) = \sin^2(7\theta) \approx 0.961
$$

Running `src/grover.py` with 2000 shots measured a hit rate of **0.967**
for the marked state `1011` — matching the closed-form prediction to
within simulation noise, confirming the circuit implements the rotation
derived above rather than just "usually finding the right answer."

```
marked=['1011']         iterations=3  hit_rate=0.967   (theory: 0.961)
marked=['0110']         iterations=3  hit_rate=0.966   (theory: 0.961)
marked=['0000','1111']  iterations=2  hit_rate=0.947   (theory for M=2, k=2: ~0.962)
```

## 5. Circuit construction (`src/grover.py`)

- **`phase_oracle`**: flips the phase of each marked bitstring using X
  gates to map it onto the all-ones string, a multi-controlled-Z (built
  from `H` + `mcx` + `H`, the standard decomposition of $CCZ$-style gates
  from Toffoli/`mcx`), then undoes the X gates.
- **`diffuser`**: implements $D = H^{\otimes n}(2|0\rangle\langle 0| -
  I)H^{\otimes n}$ the same way — X gates, multi-controlled-Z, X gates,
  sandwiched between Hadamard layers.
- **`grover_circuit`**: prepares $|s\rangle$ with $H^{\otimes n}$, then
  applies `oracle` and `diffuser` alternately $k^{*}$ times before
  measuring.

## 6. Complexity and comparison to Shor's algorithm

Grover's algorithm gives a **quadratic** speedup ($O(\sqrt N)$ vs.
$O(N)$) for *unstructured* search — it applies to essentially any
decision problem framed as "find $x$ such that $f(x)=1$," with no
assumption on the structure of $f$. Shor's algorithm
(`docs/04-shors-algorithm.md`) gives an **exponential** speedup, but only
for the specific algebraic structure of periodicity (order-finding) —
period-finding via phase estimation is not a general search technique.
This contrast is a useful example of why "quantum speedup" is not a single
number: the size of the advantage depends entirely on how much structure
the problem has for a quantum algorithm to exploit.

## 7. References

- L. K. Grover, "A fast quantum mechanical algorithm for database
  search," *Proceedings of the 28th Annual ACM Symposium on Theory of
  Computing (STOC)*, 1996.
- M. A. Nielsen & I. L. Chuang, *Quantum Computation and Quantum
  Information*, Cambridge University Press, ch. 6.
- C. Zalka, "Grover's quantum searching algorithm is optimal," *Physical
  Review A*, 60(4), 1999 (the matching lower bound).
