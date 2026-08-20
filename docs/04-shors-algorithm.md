# Shor's Algorithm — Mathematical Foundations

## 1. Overview of the reduction

Shor's algorithm factors a composite integer `N` in two stages:

1. **Classical reduction:** factoring `N` is reduced to finding the
   multiplicative order of a randomly chosen `a` mod `N`.
2. **Quantum order-finding:** the order is found using quantum phase
   estimation applied to a modular-exponentiation unitary.

Only step 2 needs a quantum computer. Step 1 is pure number theory and
runs in polynomial time classically.

---

## 2. Reducing factoring to order-finding

Let `N` be composite and odd (even `N` is trivially divisible by 2; this
case is excluded up front). Pick `a` uniformly at random from
`{2, ..., N-1}`.

**Step 0 — GCD check.** Compute `gcd(a, N)` classically (Euclidean
algorithm, polynomial time). If `gcd(a, N) ≠ 1`, it is already a
non-trivial factor of `N` — done, no quantum computer needed.

**Step 1 — Order-finding.** If `gcd(a, N) = 1`, find the multiplicative
order `r` of `a` mod `N`: the smallest positive integer such that

```
a^r ≡ 1 (mod N)
```

Such an `r` always exists because `a` is a unit in `(Z/NZ)^×`, a finite
group, so some power of `a` returns to the identity.

**Step 2 — Extract factors.** Suppose `r` is even (if not, resample `a` —
see the success-probability argument below). Then:

```
a^r - 1 ≡ 0 (mod N)
(a^(r/2) - 1)(a^(r/2) + 1) ≡ 0 (mod N)
```

Let `x = a^(r/2) mod N`. If `x ≢ -1 (mod N)` (resample `a` if it is), then
`N` divides `(x-1)(x+1)` but — because `r` is the *minimal* order — `N`
divides neither `x-1` nor `x+1` alone. A composite `N` dividing a product
without dividing either factor means `N` must be "split" between the two
factors, so:

```
gcd(x - 1, N)   and   gcd(x + 1, N)
```

are both non-trivial (i.e. `∉ {1, N}`) factors of `N`, computable
classically via the Euclidean algorithm.

### Why this succeeds with high probability

For `N` a product of two distinct odd primes (the RSA case), a
group-theoretic argument (via the structure of `(Z/NZ)^×` as a product of
cyclic groups, one per prime factor, by the CRT) shows that for `a` chosen
uniformly at random and coprime to `N`, the probability that `r` is even
**and** `a^(r/2) ≢ -1 (mod N)` is at least `1 - 1/2^(k-1)`, where `k` is
the number of distinct prime factors of `N`. For `k = 2`, this is at least
`1/2` per attempt — so a handful of independent trials with fresh random
`a` succeeds with overwhelming probability. This is why the algorithm is
*randomized*: a "bad" `a` just means retry, not failure.

---

## 3. Quantum order-finding via phase estimation

This is the only step requiring a quantum computer. The goal: given the
unitary `U_a` defined by

```
U_a |y> = |a·y mod N>          (for y < N; extended arbitrarily for y ≥ N
                                 if extra qubits are used, as in this repo's
                                 4-qubit register over residues mod 15)
```

find the order `r` of `a`.

### 3.1 Eigenstructure of U_a

Define, for `s = 0, 1, ..., r-1`:

```
|u_s> = (1/√r) * Σ_{k=0}^{r-1}  exp(-2πi·s·k/r) |a^k mod N>
```

Direct computation shows `U_a |u_s> = exp(2πi·s/r) |u_s>` — each `|u_s>`
is an eigenvector of `U_a` with eigenvalue `exp(2πi·s/r)`. The order `r`
is encoded in the *phase* of these eigenvalues. This is precisely the
setup quantum phase estimation is built for: given (access to controlled
powers of) a unitary and one of its eigenvectors, estimate the eigenvalue.

Crucially:

```
(1/√r) * Σ_{s=0}^{r-1} |u_s> = |1>
```

So preparing the auxiliary register in the simple, easy-to-prepare state
`|1>` (a single `X` gate — see `qc.x(n_count)` in `src/shor.py`) is
*exactly* an equal superposition over all the eigenvectors `|u_s>` at
once. This sidesteps ever needing to construct an individual `|u_s>`
directly.

### 3.2 Phase estimation circuit

With an `n_count`-qubit counting register and the auxiliary register
prepared in `|1> = (1/√r)Σ_s |u_s>`:

**Step A — Superposition.** Apply `H^⊗n_count` to the counting register:

```
(1/√(2^n)) * Σ_{j=0}^{2^n - 1} |j> ⊗ |1>
```

**Step B — Controlled modular exponentiation.** Apply controlled-`U_a^(2^k)`
from counting qubit `k` onto the auxiliary register, for
`k = 0, ..., n_count-1` (this is exactly the loop in
`build_shor_circuit`: `qc.append(controlled_amod15_power(a, q), ...)`).
Writing `j` in binary as `j = j_{n-1}...j_1 j_0`, this applies
`U_a^(j_{n-1}2^{n-1} + ... + j_0 2^0) = U_a^j` controlled on the counting
register being in state `|j>`. Expanding `|1>` in the eigenbasis:

```
(1/√(2^n)) Σ_j |j> ⊗ (1/√r) Σ_s exp(2πi·s·j/r) |u_s>
```

This is entanglement between the counting register and the auxiliary
register (see `docs/02-entanglement-measurement.md`): each `j`-branch of
the counting register has picked up a phase `exp(2πi·s·j/r)` correlated
with each eigenstate component.

**Step C — Inverse QFT.** Regrouping by `s` and applying the inverse QFT
(`src/qft.py::inverse_qft_gate`) to the counting register converts the
phase `s/r` encoded across the superposition into peaked measurement
probabilities: measuring the counting register yields, with probability
`≥ 4/π² ≈ 0.405` (for the best-approximating integer), a value `y` such
that

```
y / 2^n  ≈  s / r
```

for some (unknown, uniformly-distributed-over-trials) `s` coprime-ish to
`r`. This is the interference step: the inverse QFT constructively
combines amplitudes near the true phase `s/r` and destructively cancels
amplitudes elsewhere — the source of the quantum speedup, since no
individual measurement or classical computation directly "computed" `r`;
it emerged from interference across the full superposition.

### 3.3 Classical continued fractions

Given the measured `y`, compute the continued-fraction expansion of
`y / 2^n` and take convergents `p/q` (each in lowest terms) with
`q < N`. One of these convergents satisfies `q = r` (or a divisor of `r`)
with high probability, because `s/r` in lowest terms is guaranteed to
appear as a convergent of any sufficiently close approximation `y/2^n`
when `2^n > N²` (a standard result in Diophantine approximation).
This is implemented directly in `src/shor.py::phase_to_order` via Python's
`fractions.Fraction(...).limit_denominator(N)`.

Because the measured `s` may share a common factor with `r`, `q` may
recover a proper divisor of `r` rather than `r` itself — this is why
`find_factors` in this repo tries the top several measured bitstrings by
frequency rather than trusting a single shot.

---

## 4. Complexity

- **Classical part** (steps 0, 2, and continued fractions): all
  polynomial in `log N` via the Euclidean algorithm and standard continued
  fraction expansion — `O((log N)²)` to `O((log N)³)` depending on the
  multiplication algorithm used.
- **Quantum part:** the QFT on `n = O(log N)` qubits costs `O(n²)` gates
  (see `docs/03-quantum-fourier-transform.md`). The dominant cost is
  controlled modular exponentiation, which (using efficient reversible
  arithmetic circuits — adders and multipliers built from quantum
  full-adders) costs `O(n³)` (or `O(n² log n)` with more advanced
  arithmetic), giving an overall runtime of `Õ((log N)³)` — polynomial in
  the input size `log N`.
- **Classical factoring** (general number field sieve) runs in
  `L_N[1/3, (64/9)^{1/3}]`, a *sub-exponential but super-polynomial*
  function of `log N`. Shor's polynomial-time algorithm is an exponential
  asymptotic improvement.

This repository's `src/modexp_mod15.py` deliberately does **not**
implement the general `O(n³)` reversible arithmetic circuit — it hardcodes
`N=15` as an explicit 4-qubit permutation, since building and simulating a
general modular-exponentiation circuit for cryptographically relevant `N`
(hundreds to thousands of bits) is far beyond what a classical simulator
can handle. The complexity analysis above describes the general
algorithm; this repo verifies its *logical structure* end to end on the
largest instance that is both fully simulable and fully checkable by hand.

---

## 5. Worked numeric example: N = 15, a = 7

This matches exactly what `python src/shor.py` runs.

1. `gcd(7, 15) = 1` ✓, proceed.
2. Powers of 7 mod 15: `7^1=7, 7^2=4, 7^3=28 mod 15=13, 7^4=91 mod 15=1`.
   So the order is `r = 4`.
3. `r = 4` is even. Compute `x = 7^(4/2) mod 15 = 7^2 mod 15 = 4`.
4. Check `x ≠ -1 mod 15` (i.e. `4 ≠ 14`) ✓.
5. Factors: `gcd(4-1, 15) = gcd(3, 15) = 3`, and
   `gcd(4+1, 15) = gcd(5, 15) = 5`.
6. `15 = 3 × 5`. ✓ — matches the measured output of `find_factors(7)` in
   this repo, which recovers `r ∈ {1, 4}` from the circuit's measurement
   statistics and correctly returns `factors = [3, 5]`.

The quantum circuit's job in this example is entirely encapsulated in step
2: finding `r = 4` without classically computing `7^1, 7^2, 7^3, 7^4` one
at a time and checking each against 1 — instead, phase estimation extracts
the periodicity of the sequence `7^k mod 15` via interference across a
superposition prepared and measured in a single circuit execution.

---

## 6. References

- P. W. Shor, "Polynomial-Time Algorithms for Prime Factorization and
  Discrete Logarithms on a Quantum Computer," *SIAM Journal on Computing*,
  26(5), 1997, pp. 1484–1509.
- M. A. Nielsen & I. L. Chuang, *Quantum Computation and Quantum
  Information*, Cambridge University Press, ch. 5.
- A. Ekert & R. Jozsa, "Quantum computation and Shor's factoring
  algorithm," *Reviews of Modern Physics*, 68(3), 1996.
