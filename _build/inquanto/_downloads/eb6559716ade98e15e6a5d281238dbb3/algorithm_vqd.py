r"""Variational Quantum Deflation using computables."""

# imports
from numpy import asarray
from pytket.extensions.qiskit import AerBackend, AerStateBackend

from inquanto.algorithms import AlgorithmVQE
from inquanto.algorithms.vqd import AlgorithmVQD
from inquanto.ansatzes import FermionSpaceAnsatzkUpCCGSD
from inquanto.computables.atomic import ExpectationValue, OverlapSquared
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import MinimizerScipy
from inquanto.protocols.averaging._pauli_averaging import PauliAveraging
from inquanto.protocols.statevector._sparse_sv import SparseStatevectorProtocol
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState

# initialize the system
h2 = load_h5("h2_sto3g.h5")
fermion_hamiltonian = h2["hamiltonian_operator"]
qubit_hamiltonian = QubitMappingJordanWigner().operator_map(fermion_hamiltonian)
space = FermionSpace(4)
state = FermionState([1, 1, 0, 0])

# choose ansatz and minimizer
ansatz = FermionSpaceAnsatzkUpCCGSD(space, state, k_input=2)
minimizer = MinimizerScipy(method="COBYLA")

# run a vqe first: set up expectation value to minimize
expectation_value = ExpectationValue(ansatz, qubit_hamiltonian)
# instantiate AlgorithmVQE
vqe = AlgorithmVQE(
    minimizer,
    expectation_value,
    initial_parameters=ansatz.state_symbols.construct_random(seed=0),
)
# build the algorithm
backend = AerBackend()
vqe.build(protocol_objective=PauliAveraging(backend, shots_per_circuit=10000))
# execute
vqe.run()
# print the results
print("VQE Energy:    ", vqe.final_value)
# symbol values to create the ansatz for the ground state
print("VQE Final Parameters:", asarray(list(vqe.final_parameters.values())))

# create deflationary ansatz which matches the vqe ansatz
ansatz_2 = ansatz.copy()

# modify the symbols pytket protocols can distinguish between the wavefunctions
ansatz_2.symbol_substitution(r"{}_2")

# create expectation value of excited states you wish to evaluate the energy of
expectation_value = ExpectationValue(ansatz_2, qubit_hamiltonian)

# choose the deflation scheme you wish to follow by defining a means to find the initial weight
weight_expression = ExpectationValue(ansatz_2, -1 * qubit_hamiltonian)

# define the variational penalty expression, for VQD, the variational part is the overlap
overlap_expression = OverlapSquared(ansatz, ansatz_2)

# instantiate VQD object
vqd = AlgorithmVQD(
    objective_expression=expectation_value,
    overlap_expression=overlap_expression,
    weight_expression=weight_expression,
    minimizer=MinimizerScipy(method="COBYLA"),
    initial_parameters=ansatz_2.state_symbols.construct_random(seed=0),
    vqe_value=vqe.final_value,
    vqe_parameters=vqe.final_parameters,
    n_vectors=3,  # generate 3 excited states
)
# Build circuits and expression tree for the necessary computables.
# Each computable expression can be allocated a specific protocol.
# It is recommended to try more statevector protocols or replacing the overlap squared protocol with
# the shot based ComputeUncompute or SwapTest
vqd.build(
    objective_protocol=PauliAveraging(backend, shots_per_circuit=10000),
    weight_protocol=PauliAveraging(backend, shots_per_circuit=10000),
    overlap_protocol=SparseStatevectorProtocol(AerStateBackend()),
)

# execute
vqd.run()

# print results
print("VQD excited state energies:   ", vqd.final_values)
SV_energies = [
    -1.1368465754696442,
    -0.4951737702568179,
    -0.13583641088346535,
    0.5515572309175806,
]
print("SV VQD excited state energies:", SV_energies)
