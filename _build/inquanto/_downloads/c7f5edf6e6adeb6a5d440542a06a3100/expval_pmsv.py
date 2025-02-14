r"""Example using PMSV error mitigation to calculate expectation values."""

# imports
from pytket.partition import PauliPartitionStrat
from pytket.extensions.qiskit import AerBackend

from inquanto.protocols import PMSV
from inquanto.ansatzes import FermionSpaceStateExpChemicallyAware
from inquanto.protocols import PauliAveraging
from inquanto.express import load_h5, get_noisy_backend
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.spaces import QubitSpace

# get an example system from express database
h2 = load_h5("h2_sto3g_symmetry.h5", as_tuple=True)

# get fermionic objects
hamiltonian = h2.hamiltonian_operator
space = h2.fermion_space
state = h2.hf_state
# map to jw qubit hamiltonian
kernel = hamiltonian.qubit_encode()

# variables for shot based sampling
seed = 5
shots = 10000

# get an AerBackend with a simple NoiseModel preloaded into it
# this simple model only applies depolarising error to CNOT gates and
# readout error
noisier_backend = get_noisy_backend(h2.n_orbital * 2)


# To perform partition measurement symmetry verification we need a set of
# Z2 symmetries of the operator
symmetries = QubitSpace(h2.n_orbital * 2).symmetry_operators_z2_in_sector(
    kernel, QubitMappingJordanWigner.state_map(state)
)

# these symmetries are qubit operators
print(symmetries)

# prepare a compact chemical ansatz
exponents = space.construct_single_ucc_operators(state)
# the above adds nothing due to the symmetry of the system
exponents += space.construct_double_ucc_operators(state)
ansatz = FermionSpaceStateExpChemicallyAware(exponents, state)

# get a dictionary to insert numerical values for the free_symbols
p = ansatz.state_symbols.construct_random(seed=seed)
print(p)

# initialize the protocol for the shot based backend
# to see the effect of PMSV, use the backend with the error model
protocol = PauliAveraging(
    # noisier_backend, #or
    AerBackend(),
    shots_per_circuit=shots,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)

# prepare the PMSV class
mitms_pmsv = PMSV(symmetries)

# build the measurement circuits, including the PMSV modification
# run the circuit shots
protocol.build(p, ansatz, kernel, noise_mitigation=mitms_pmsv).compile_circuits().run(
    seed=seed
)
# we can inspect the allocation of the qubit operators to the measurement circuits
print(protocol.dataframe_partitioning())
# use the error mitigated results to evaluate the expectation value
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("NOISELESS (PMSV): ", energy_value)
# we can inspect the expectation values and uncertainty of all the qubit operators in the
# measurement circuits, including the stabilizers
print(protocol.dataframe_measurements())
