r"""A canonical VQE simulation of H2 in STO-3G using a UCCSD Ansatz."""

from pytket import OpType

from inquanto.algorithms import AlgorithmVQE
from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.computables import ExpectationValue, ExpectationValueDerivative
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import MinimizerScipy
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState

from qnexus.models import AerStateConfig
from qnexus.client import projects, auth

auth.login()

project_ref = projects.get_or_create(
    name=f"VQE Demo using UCCSD Ansatz",
    description="a demo project",
    properties={},
)

# Load in the system from the express module.
h2 = load_h5("h2_sto3g.h5", as_tuple=True)

# Generate a qubit Hamiltonian from the fermionic Hamiltonian stored in the express module.
hamiltonian_operator = h2.hamiltonian_operator
mapping = QubitMappingJordanWigner()
qubit_operator = mapping.operator_map(hamiltonian_operator)

# In order to construct an ansatz we need to create a space and a state object.
space = FermionSpace(4)
state = FermionState([1, 1, 0, 0], 1)

ansatz = FermionSpaceAnsatzUCCSD(space, state)
print("Parameters in the ansatz: ", list(ansatz.free_symbols_ordered()))

# Create the computable for the cost function (the energy)
expectation_value = ExpectationValue(ansatz, qubit_operator)
# Create the computable for the derivative of the cost function wrt the free parameters of the ansatz
gradient_expression = ExpectationValueDerivative(
    ansatz, qubit_operator, ansatz.free_symbols_ordered()
)

# initialize the algorithm, supplying a set of initial parameters for the ansatz
# here our optimization process only uses the total energy, not the gradients
vqe = AlgorithmVQE(
    objective_expression=expectation_value,
    minimizer=MinimizerScipy(),
    initial_parameters=ansatz.state_symbols.construct_random(
        seed=0, mu=0.0, sigma=0.01
    ),
    gradient_expression=gradient_expression,
)

vqe.build(
    protocol_objective=SparseStatevectorProtocol(
        backend=AerStateConfig(), project_ref=project_ref
    ),
    protocol_gradient=SparseStatevectorProtocol(
        backend=AerStateConfig(), project_ref=project_ref
    ),
).run()

print("Minimum Energy: {}".format(vqe.final_value))
vqe.generate_report_params(vqe.final_parameters)
