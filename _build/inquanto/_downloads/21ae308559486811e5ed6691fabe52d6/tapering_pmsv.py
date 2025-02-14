r"""Using Hamiltonian symmetries to reduce the qubit count with tapering, and perform noise mitigation with PMSV."""
from inquanto.extensions.pyscf import ChemistryDriverPySCFMolecularRHF, FromActiveSpace
from inquanto.spaces import QubitSpace
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.symmetry import TapererZ2
from inquanto.express import get_noisy_backend
from inquanto.computables import ExpectationValue
from inquanto.protocols import PauliAveraging, PMSV
from pytket.partition import PauliPartitionStrat

# Define H2O system with (6,5) active space. Qubit-encode with JW
driver = ChemistryDriverPySCFMolecularRHF(  # 10 electrons in 7 spatial orbs before active space reduction
    geometry=[
        ["O", [0.0, 0.0, 0.127]],
        ["H", [0.0, 0.758, -0.509]],
        ["H", [0.0, -0.758, -0.509]],
    ],
    basis="sto3g",
    point_group_symmetry=True,
    frozen=FromActiveSpace(ncas=5, nelecas=6),
)
jw = QubitMappingJordanWigner()
fermion_ham, fermion_space, hf_state = driver.get_system()
ham = fermion_ham.qubit_encode(mapping=jw)

# Initialize a simple chemical ansatz
ansatz_uccsd = FermionSpaceAnsatzUCCSD(
    fermion_space=fermion_space, fermion_state=hf_state, qubit_mapping=jw
)

# Find Z2 symmetries of the hamiltonian
symmetry_operators = QubitSpace.symmetry_operators_z2(ham)
symmetry_sectors = [
    x.symmetry_sector(QubitMappingJordanWigner.state_map(hf_state))
    for x in symmetry_operators
]
print(f"{len(symmetry_operators)} Z2 symmetries found:")
[print(s) for s in symmetry_operators]

# Initialize taperer using first 2 Z2 symmetries. We'll save the other two to use for PMSV
taperer = TapererZ2(symmetry_operators[:2], symmetry_sectors[:2])

# Apply tapering to hamiltonian and ansatz
ham_tapered = taperer.tapered_operator(ham, relabel_qubits=True)
ansatz_tapered = FermionSpaceAnsatzUCCSD(
    fermion_space,
    hf_state,
    taperer=taperer,
)

print(f"\nUn-tapered:")
print(f"\tNum hamiltonian terms: {len(ham)}")
print(f"\t{ansatz_uccsd.generate_report()}")
print(f"Tapered:")
print(f"\tNum hamiltonian terms: {len(ham_tapered)}")
print(f"\t{ansatz_tapered.generate_report()}")

# Calculate the energy with a noisy backend using PMSV noise mitigation
noisy_backend = get_noisy_backend(ansatz_tapered.n_qubits, cx_err=0.001, ro_err=0.001)

# Get symmetries in the tapered qubit space
symmetries_tapered = QubitSpace.symmetry_operators_z2_in_sector(
    ham_tapered,
    taperer.tapered_state(
        QubitMappingJordanWigner.state_map(hf_state), relabel_qubits=True
    ),
)
pmsv = PMSV(symmetries_tapered)

# Use a random set of parameters
params = ansatz_tapered.state_symbols.construct_random(seed=0)

# Use the shot-based PauliAveraging protocol to reduce the number of measurements
energy = ExpectationValue(ansatz_tapered, ham_tapered)
protocol = PauliAveraging(
    backend=noisy_backend,
    shots_per_circuit=1000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)
print("\nBuilding circuits...")
protocol.build_from(
    parameters=params,
    computable=energy,
    noise_mitigation=pmsv,  # try removing this to see effects of noise mitigation
).compile_circuits()

print("\nRunning circuits...")
protocol.run(seed=0)

expval = energy.evaluate(protocol.get_evaluator())
print(f"\nNoisy energy = {expval} Ha")
print(f"Statevector energy = {energy.default_evaluate(params)} Ha")

# print(protocol.dataframe_measurements())
