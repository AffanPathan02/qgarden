# Entanglement, Measurement, and Why Shor's Algorithm Needs Both

## Entanglement

A multi-qubit state is **entangled** if it cannot be written as a tensor
product of individual qubit states. The canonical example, a Bell pair:

```
|Φ+> = (|00> + |11>) / √2
```

cannot be factored as `|ψ_1> ⊗ |ψ_2>` for any single-qubit states `ψ_1,
ψ_2` — measuring one qubit instantaneously determines the outcome of
measuring the other, even though neither qubit has a definite state on its
own beforehand.

## Where entanglement appears in this repository

The phase-estimation circuit in `src/shor.py` entangles two registers:

- an `n_count`-qubit **counting register**, prepared in equal superposition
  by Hadamards,
- a 4-qubit **auxiliary register**, holding residues mod 15.

The controlled modular-exponentiation gates
(`modexp_mod15.controlled_amod15_power`) entangle these registers: each
counting qubit becomes correlated with a different power `a^(2^k) mod 15`
applied to the auxiliary register. This entanglement is what lets a single
run of the circuit implicitly encode information about *all* the powers of
`a` mod 15 simultaneously — the auxiliary register is never measured, but
its correlation with the counting register is what the inverse QFT
extracts.

## Measurement and the role of interference

Only the counting register is measured (`qc.measure` in `build_shor_circuit`).
Because of the entanglement above, tracing out the auxiliary register
leaves the counting register in a state whose amplitudes are shaped by the
period `r` (the multiplicative order of `a` mod 15). The inverse QFT
converts this periodic structure into constructive interference at
specific measurement outcomes — this is the actual "speedup" step: a
classical computer would need to compute `a^k mod 15` for many `k` and
inspect them one at a time to find the period, whereas the quantum circuit
extracts periodicity via interference across a superposition prepared in a
single circuit execution.

`src/shor.py::find_factors` shows this concretely: running the circuit
with `shots=20` and inspecting the measured bitstrings recovers the order
`r` with high probability, from which the classical `gcd` post-processing
step recovers the factors of 15.

## Further reading

- Nielsen & Chuang, ch. 2.6 (entanglement), ch. 5.4.1 (order-finding /
  phase estimation).
