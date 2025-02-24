r"""A canonical VQE simulation of H2 in STO-3G using a hardware-efficient Ansatz."""

# imports
from pytket import OpType
from pytket.extensions.qiskit import AerStateBackend

from inquanto.algorithms import AlgorithmVQE
from inquanto.ansatzes import HardwareEfficientAnsatz
from inquanto.computables import ExpectationValue
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import MinimizerScipy
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.spaces import FermionSpace
from inquanto.states import QubitState

# Load in the system from the express module.
h2 = load_h5("h2_sto3g.h5", as_tuple=True)

# Generate a qubit Hamiltonian from the fermionic Hamiltonian stored in the express module.
hamiltonian_operator = h2.hamiltonian_operator
mapping = QubitMappingJordanWigner()
qubit_operator = mapping.operator_map(hamiltonian_operator)

# In order to construct an ansatz we need to create a space and a state object.
space = FermionSpace(4)
state = QubitState([1, 1, 0, 0])

# Instantiate the HEA ansatz object with a list of gate types, a state and the number of layers.
# Here we use pytket OpTypes to define the rotation operators for the HEA and construct with 2 layer
ansatz = HardwareEfficientAnsatz([OpType.Rx, OpType.Ry], state, 2)

# Create the computable for the quantity of interest, then build and run the algorithm.
expectation_value = ExpectationValue(ansatz, qubit_operator)

# initialize the algorithm, supplying a set of initial parameters for the HEA ansatz
# here our optimization process only uses the total energy, not the gradients
vqe = AlgorithmVQE(
    objective_expression=expectation_value,
    minimizer=MinimizerScipy(),
    initial_parameters=ansatz.state_symbols.construct_random(
        seed=0, mu=0.0, sigma=0.01
    ),
)
vqe.build(
    protocol_objective=SparseStatevectorProtocol(AerStateBackend()),
).run()

print("Minimum Energy: {}".format(vqe.final_value))
vqe.generate_report_params(vqe.final_parameters)
