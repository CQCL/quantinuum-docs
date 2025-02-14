r"""Simple shot-based energy calculation using a double factorized hamiltonian."""

# imports
from pytket.extensions.qiskit import AerBackend
from pytket.partition import PauliPartitionStrat

from inquanto.computables import ExpectationValue
from inquanto.express import get_system
from inquanto.ansatzes import (
    FermionSpaceAnsatzUCCSD,
    rotate_ansatz_restricted,
)
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.protocols import PauliAveraging
from inquanto.computables.composite import ExpectationValueSumComputable

# Note: for a small system like this, we don't expect double factorization reduce the number of circuits
ham, space, state = get_system("h2_631g.h5")

# Truncate 2e integrals such that every element is within 1e-3 of exact val
df_ham = ham.double_factorize(tol1=1e-3, tol2=-1, method="cho")
jw = QubitMappingJordanWigner()

# Test a single ansatz configuration (random parameters)
ansatz = FermionSpaceAnsatzUCCSD(space, state, jw)
params = ansatz.state_symbols.construct_random(seed=1)
backend = AerBackend()

# Perform basis rotations, and map to qubit operators for each hamiltonian term
# (see https://docs.quantinuum.com/inquanto/manual/spaces.html#double-factorization)
df_energy_computable = ExpectationValueSumComputable(
    [rotate_ansatz_restricted(ansatz, rot) for rot in df_ham.rotation_matrices()],
    [fo.qubit_encode() for fo in df_ham.fermion_operators()],
)

# Build circuits for measuring total energy. Note that PauliAveraging supports a single ansatz, so we use the
# build_protocols_from() method to collect all circuits into a ProtocolList, with one protocol for each rotated ansatz.
protocols = PauliAveraging.build_protocols_from(
    params,
    df_energy_computable,
    backend=backend,
    shots_per_circuit=10000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)
protocols.compile_circuits()

# Run circuits and calculate energy
protocols.run(seed=1)
e = df_energy_computable.evaluate(protocols.get_evaluator())
print("** Double Factorized **")
print("Total energy: ", e)
print("Number of circuits: ", protocols.n_circuit)
print("Circuit depth: ", [c.depth() for c in protocols.get_circuits()])

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
print("\n** Non-factorized **")
print("Total energy: ", e)
print("Number of circuits: ", protocols.n_circuit)
print("Circuit depth: ", [c.depth() for c in protocols.get_circuits()])

# compare to statevector, so we can see the impact of shot-noise
print("\n** Non-factorized (SV) **")
print("Total energy: ", energy_computable.default_evaluate(params))
