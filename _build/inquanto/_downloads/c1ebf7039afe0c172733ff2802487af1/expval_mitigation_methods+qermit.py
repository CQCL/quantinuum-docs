r"""Running protocols via Qermit's MitRes and MitEx and inquanto's noise mitigation."""

# imports
from pytket.extensions.qiskit import AerBackend
from pytket.partition import PauliPartitionStrat

from qermit.spam import gen_UnCorrelated_SPAM_MitRes

# from qermit.zero_noise_extrapolation import gen_ZNE_MitEx

from inquanto.protocols import PMSV, SPAM
from inquanto.ansatzes import FermionSpaceStateExpChemicallyAware
from inquanto.operators import QubitOperator
from inquanto.protocols import PauliAveraging
from inquanto.express import load_h5
from inquanto.spaces import FermionSpace, QubitSpace
from inquanto.states import FermionState
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.symmetry import PointGroup
from inquanto.express import get_noisy_backend


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


# To perform partition measurement symmetry verification (PMSV) we need a set of
# Z2 symmetries of the operator
stabilizers = QubitSpace(h2.n_orbital * 2).symmetry_operators_z2_in_sector(
    kernel, QubitMappingJordanWigner.state_map(state)
)

# these symmetries are qubit operators
print(stabilizers)

# prepare a compact chemical ansatz
exponents = space.construct_single_ucc_operators(state)
# the above adds nothing due to the symmetry of the system
exponents += space.construct_double_ucc_operators(state)
ansatz = FermionSpaceStateExpChemicallyAware(exponents, state)

# get a dictionary to insert numerical values for the free_symbols
p = ansatz.state_symbols.construct_random(seed=seed)
print(p)
######


# instance a protocol with noiseless shot based backend
protocol_noiseless_template = PauliAveraging(
    AerBackend(),
    shots_per_circuit=shots,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)

# instance a protocol with simple noise model shot based backend
protocol_noisy_template = PauliAveraging(
    noisier_backend,
    shots_per_circuit=shots,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)

# create a dump of the protocol as a template to save reinstantiating later
noiseless_protocol_pickle = protocol_noiseless_template.dumps()
noisy_protocol_pickle = protocol_noisy_template.dumps()

# copy the protocol template
protocol = PauliAveraging.loads(noiseless_protocol_pickle, AerBackend())

# build measurement circuits without error mit for noiseless backend
# run shots and inspect noiseless results
protocol.build(p, ansatz, kernel, noise_mitigation=None).compile_circuits().run(
    seed=seed
)
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("noiseless: ", energy_value)
noiseless_df = protocol.dataframe_measurements()
print(protocol.dataframe_measurements())
print(protocol.dataframe_circuit_shot())
print("")


# build measurement circuits without error mit for noiseless backend
# run shots and inspect noiseless results
protocol = PauliAveraging.loads(noiseless_protocol_pickle, AerBackend())
# instance inquanto pmsv class using the Z2 symmetries
mitms_pmsv = PMSV(stabilizers)
protocol.build(p, ansatz, kernel, noise_mitigation=mitms_pmsv).compile_circuits().run(
    seed=seed
)
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("NOISELESS (PMSV): ", energy_value)
print(protocol.dataframe_measurements())
# pmsv should do nothing to noiseless runs -> should be equality/true
print(noiseless_df == protocol.dataframe_measurements())
# note that the stabilizers are measured by every measurement circuit
# so you end up with M x shots_per_circuit results for them
# and for noisefree their Pauli expectation = their parity
print(protocol.dataframe_circuit_shot())
print("")


# build measurement circuits without error mit for simple noisy backend
# run shots and inspect noisy results
protocol = PauliAveraging.loads(noisy_protocol_pickle, noisier_backend)
protocol.build(p, ansatz, kernel, noise_mitigation=None).compile_circuits().run(
    seed=seed
)
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("Unmitigated noisy: ", energy_value)
print(protocol.dataframe_measurements())
print("")


# build modified measurement circuits for simple noisy backend
# clean noisy results using PMSV filtering here
protocol = PauliAveraging.loads(noisy_protocol_pickle, noisier_backend)
mitms_pmsv = PMSV(stabilizers)
protocol.build(p, ansatz, kernel, noise_mitigation=mitms_pmsv).compile_circuits().run(
    seed=seed
)
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("NOISY (PMSV): ", energy_value)
# note sample size will be less than shots per circuit due to pmsv discard
print(protocol.dataframe_measurements())
print("")


# build measurement circuits for simple noisy backend
# apply SPAM to improve the expectation values
protocol = PauliAveraging.loads(noisy_protocol_pickle, noisier_backend)
mitms_spam = SPAM(backend=noisier_backend).calibrate(calibration_shots=5000, seed=seed)
protocol.build(p, ansatz, kernel, noise_mitigation=mitms_spam).compile_circuits().run(
    seed=seed
)
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("NOISY (SPAM): ", energy_value)
print(protocol.dataframe_measurements())
print("")


# build measurement circuits without error mit for simple noisy backend
# combine spam calibration and and PMSV
protocol = PauliAveraging.loads(noisy_protocol_pickle, noisier_backend)

mitms_spam = SPAM(backend=noisier_backend).calibrate(calibration_shots=5000, seed=seed)
# @ allows mitms to run in sequence
protocol.build(
    p, ansatz, kernel, noise_mitigation=mitms_pmsv @ mitms_spam
).compile_circuits().run(seed=seed)
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("double mitigation pmsv then spam: ", energy_value)
print(protocol.dataframe_measurements())
print("")
# Note: mitms_spam @ mitms_pmsv is not supported at the moment.

print("")
print("Error mitigation from Qermit")
protocol = PauliAveraging.loads(noisy_protocol_pickle, noisier_backend)
protocol.build(p, ansatz, kernel, noise_mitigation=None)
protocol.compile_circuits()
uc_spam_mitres = gen_UnCorrelated_SPAM_MitRes(
    backend=noisier_backend, calibration_shots=5000, seed=seed
)
protocol.run_mitres(uc_spam_mitres, {})
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("Qermit MitRes (SPAM): ", energy_value)
print(protocol.dataframe_measurements())
print("")

# build measurement circuits error mit for simple noisy backend
# combine spam calibration from qermit and PMSV in inquanto
protocol = PauliAveraging.loads(noisy_protocol_pickle, noisier_backend)
protocol.build(p, ansatz, kernel, noise_mitigation=mitms_pmsv)
protocol.compile_circuits()
uc_spam_mitres = gen_UnCorrelated_SPAM_MitRes(
    backend=noisier_backend, calibration_shots=5000, seed=seed
)
protocol.run_mitres(uc_spam_mitres, {})
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("Qermit MitRes (SPAM) and inq pmsv: ", energy_value)
print(protocol.dataframe_measurements())
