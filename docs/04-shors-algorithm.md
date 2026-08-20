# Shor's Algorithm

## The problem: factoring via order-finding

Shor's algorithm factors an integer `N` by reducing factoring to
**order-finding**: given `a` coprime to `N`, find the smallest `r > 0`
such that `a^r ≡ 1 (mod N)`. Once `r` is known:

- If `r` is even and `a^(r/2) ≢ -1 (mod N)`, then `gcd(a^(r/2) - 1, N)` and
  `gcd(a^(r/2) + 1, N)` are (with high probability) non-trivial factors of
  `N`. This works because `a^r - 1 = (a^(r/2)-1)(a^(r/2)+1) ≡ 0 (mod N)`,
  so `N` divides that product without (generically) dividing either factor
  alone — meaning `N` must share a nontrivial common factor with each.

Classically, order-finding is believed to be as hard as factoring itself —
no known classical algorithm does it in polynomial time. Shor's
contribution was showing order-finding **can** be done in polynomial time
on a quantum computer, via quantum phase estimation.

## How the pieces in this repo fit together

1. **`src/modexp_mod15.py`** builds the controlled unitary `U_a` where
   `U_a|y> = |a·y mod 15>`. Its eigenvalues encode the order `r` of `a` mod
   15: eigenvector `|u_s> = (1/√r) Σ_k e^{-2πi·s·k/r} |a^k mod 15>` has
   eigenvalue `e^{2πi·s/r}`.
2. **`src/shor.py::build_shor_circuit`** runs quantum phase estimation
   against `U_a`: a counting register in superposition controls successive
   powers `U_a^(2^0), U_a^(2^1), ...` applied to an auxiliary register
   prepared in `|1>` (a specific superposition of eigenvectors), then
   `src/qft.py`'s inverse QFT converts the resulting phase into a
   measurable value.
3. **`src/shor.py::phase_to_order`** takes the measured bitstring, treats
   it as a binary fraction `φ`, and uses a continued-fraction expansion
   (`Fraction(...).limit_denominator(15)`) to recover the denominator `r` —
   this is the standard classical post-processing step of the algorithm.
4. **`src/shor.py::find_factors`** applies the `gcd` step above to recover
   the actual factors.

Running `python src/shor.py` factors 15 as 3 × 5 for every valid choice of
`a ∈ {2, 7, 8, 11, 13}`, confirming the full pipeline — not just the
individual QFT/entanglement pieces — works end to end.

```
a= 7 -> order candidates tried: [1, 4] | factors found: [3, 5]
a= 2 -> order candidates tried: [1, 4] | factors found: [3, 5]
a= 8 -> order candidates tried: [1, 4] | factors found: [3, 5]
a=11 -> order candidates tried: [2]    | factors found: [3, 5]
a=13 -> order candidates tried: [1, 4] | factors found: [3, 5]
```

## What's specialised vs. general here

This implementation is **not** the general Shor's algorithm — it hardcodes
`N = 15` by writing the modular-multiplication unitary as an explicit
4-qubit permutation (`_c_amod15` in `modexp_mod15.py`), which only works
because 15 is small enough that "multiply by `a` mod 15" is just a
relabeling of 15 basis states. The general algorithm needs a reversible
modular-exponentiation circuit built from arithmetic primitives (adders,
modular multipliers), which requires many more qubits and is impractical
to simulate classically for interesting `N`. This repo's goal was to
implement and verify every conceptual piece of the algorithm — phase
estimation, the QFT, entanglement between registers, classical
continued-fraction post-processing — end to end on a case small enough to
fully understand and check, not to claim a scalable implementation.

## Complexity-theoretic implications for RSA

RSA's security rests on the assumed hardness of factoring the product of
two large primes. Shor's algorithm factors an `n`-bit integer in
`O(n²ᐧlog n ᐧ log log n)` time on a quantum computer (via fast quantum
arithmetic for the modular exponentiation step), compared to the best
known classical factoring algorithms (the general number field sieve),
which run in **sub-exponential but super-polynomial** time. A
sufficiently large, fault-tolerant quantum computer running Shor's
algorithm would break RSA (and Diffie-Hellman, and elliptic-curve
cryptography, all of which rely on related hardness assumptions) in
polynomial time — the driving motivation behind post-quantum cryptography
standardization (e.g. NIST's lattice-based ML-KEM / ML-DSA standards),
which relies on problems (like lattice problems) not currently known to
admit an efficient quantum algorithm.

## Further reading

- P. Shor, "Polynomial-Time Algorithms for Prime Factorization and
  Discrete Logarithms on a Quantum Computer," SIAM J. Computing, 1997.
- Nielsen & Chuang, ch. 5.
