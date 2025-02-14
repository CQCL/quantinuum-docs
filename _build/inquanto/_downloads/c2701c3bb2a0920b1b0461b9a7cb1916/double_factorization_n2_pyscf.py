r"""Get a double factorized hamiltonian from the PySCF extension, calculate energy, and compare to standard approach."""
from inquanto.ansatzes import (
    FermionSpaceAnsatzChemicallyAwareUCCSD,
    rotate_ansatz_restricted,
)
from inquanto.computables import ExpectationValue
from inquanto.computables.composite import ExpectationValueSumComputable
from inquanto.protocols import PauliAveraging
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.extensions.pyscf import ChemistryDriverPySCFMolecularRHF, FromActiveSpace
from pytket.partition import PauliPartitionStrat
from pytket.extensions.qiskit import AerBackend

# Build system driver. Try varying the size of the active space to see scaling behavior
driver = ChemistryDriverPySCFMolecularRHF(
    geometry=[["N", [0.0, 0.0, 0.0]], ["N", [1.1, 0.0, 0.0]]],
    basis="cc-pVDZ",
    verbose=0,
    frozen=FromActiveSpace(ncas=8, nelecas=4),
    point_group_symmetry=True,
)

# Build conventional representation of Hamiltonian
ham, space, state = driver.get_system()

# JW encoding required for double factorization
jw = QubitMappingJordanWigner()

# Consider a single ansatz configuration (random parameters)
ansatz = FermionSpaceAnsatzChemicallyAwareUCCSD(space, state)
params = ansatz.state_symbols.construct_random()

# Shot-based, noiseless simulation
backend = AerBackend()
shots = 10000
seed = 0


print("Standard hamiltonian:")
energy_computable = ExpectationValue(ansatz, ham.qubit_encode(jw))
protocol = PauliAveraging(
    backend,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
    shots_per_circuit=shots,
)
protocol.build_from(params, energy_computable).compile_circuits()
print("- num circuits: ", protocol.n_circuit)
print("- circ depth: ", [c.depth() for c in protocol.get_circuits()])

protocol.run(seed=seed)
e = energy_computable.evaluate(protocol.get_evaluator())
print("- energy: ", e)


print("\nDouble factorized hamiltonian:")
# Get double factorized hamiltonian. Approximating 2e ints to 1e-4 element-wise precision
df_ham, space, state = driver.get_double_factorized_system(
    tol1=1e-4, tol2=-1, method="cho"
)

# Perform basis rotations, and map to qubit operators (see https://docs.quantinuum.com/inquanto/manual/spaces.html#double-factorization)
states, kernels = [], []
operators = df_ham.fermion_operators()
rotations = df_ham.rotation_matrices()
for operator, rotation in zip(operators, rotations):
    states.append(rotate_ansatz_restricted(ansatz, rotation.T))
    kernels.append(operator.qubit_encode(jw))

# Build total energy computable.
energy_computable_df = ExpectationValueSumComputable(states, kernels)

# Build circuits for measuring total energy
protocols_df = PauliAveraging.build_protocols_from(
    params,
    energy_computable_df,
    backend=backend,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
    shots_per_circuit=shots,
).compile_circuits()

print("- num circuits: ", protocols_df.n_circuit)
print("- circ depth: ", [c.depth() for c in protocols_df.get_circuits()])

# Run circuits and evaluate result
protocols_df.run(seed=seed)
e_df = energy_computable_df.evaluate(protocols_df.get_evaluator())

print("- energy: ", e_df)
