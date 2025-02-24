r"""Simple shot-based energy calculation using a double factorized, unrestricted-spin hamiltonian."""

# imports
from pytket.extensions.qiskit import AerBackend
from pytket.partition import PauliPartitionStrat

from inquanto.express import get_system
from inquanto.ansatzes import (
    FermionSpaceAnsatzUCCSD,
    rotate_ansatz_generalized,
)
from inquanto.protocols import PauliAveraging
from inquanto.computables import ExpectationValue
from inquanto.computables.composite import ExpectationValueSumComputable

# Use a small, unrestricted-spin system with non-zero spin
ham, space, state = get_system("h3_sto3g_m2_u.h5")

# Truncate 2e integrals such that every element is within 1e-3 of exact val
df_ham = ham.double_factorize(tol1=1e-3, tol2=-1, method="cho")

# Test a single ansatz configuration (random parameters)
ansatz = FermionSpaceAnsatzUCCSD(space, state)
params = ansatz.state_symbols.construct_random(seed=1)
backend = AerBackend()

# Perform basis rotations, and map to qubit operators for each hamiltonian term
# (see https://docs.quantinuum.com/inquanto/manual/spaces.html#double-factorization).
# For an unrestricted system, rotation matrices in the double-factorized hamiltonian can mix spin, so we require
# generalized rotations.
df_energy_computable = ExpectationValueSumComputable(
    [rotate_ansatz_generalized(ansatz, rot) for rot in df_ham.rotation_matrices()],
    [fo.qubit_encode() for fo in df_ham.fermion_operators()],
)

# Build circuits for measuring total energy. Note that PauliAveraging supports a single ansatz, so we use the
# build_protocols_from() method to collect all circuits into a ProtocolList, with one protocol for each rotated ansatz.
df_protocols = PauliAveraging.build_protocols_from(
    params,
    df_energy_computable,
    backend=backend,
    shots_per_circuit=100000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)
df_protocols.compile_circuits()

# Run circuits and calculate energy
df_protocols.run(seed=0)
e_df = df_energy_computable.evaluate(df_protocols.get_evaluator())
print("** Double Factorized **")
print("Total energy: ", e_df)
print("Number of circuits: ", df_protocols.n_circuit)
print("Circuit depth: ", [c.depth() for c in df_protocols.get_circuits()])

# Compare to statevector, so we can see the impact of shot-noise
print("\n** Double Factorized (SV) **")
print("Total energy: ", df_energy_computable.default_evaluate(params))

# Comparing to a non-factorized hamiltonian, so we can see the implications of the truncation
energy_computable = ExpectationValue(ansatz, ham.qubit_encode())
protocols = PauliAveraging.build_protocols_from(
    params,
    energy_computable,
    backend=backend,
    shots_per_circuit=100000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)
protocols.compile_circuits()
protocols.run(seed=0)
e = energy_computable.evaluate(protocols.get_evaluator())
print("\n** non-factorized **")
print("Total energy: ", e)
print("Number of circuits: ", protocols.n_circuit)
print("Circuit depth: ", [c.depth() for c in protocols.get_circuits()])

# Compare to statevector, so we can see the impact of shot-noise
print("\n** Non-factorized (SV) **")
print("Total energy: ", energy_computable.default_evaluate(params))
