r"""A canonical VQE simulation of H2 in STO-3G using a UCCSD Ansatz."""

# imports
from pytket import OpType
from pytket.extensions.qiskit import AerStateBackend

from inquanto.algorithms import AlgorithmVQE
from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.computables import ExpectationValue, ExpectationValueDerivative
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import MinimizerScipy
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState

# In this example we will find the ground state energy of the H2 molecule in the STO-3G basis using VQE. First, we load
# in the system Hamiltonian from the express module.
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian_operator = h2.hamiltonian_operator

# Now we instantiate the space and state objects we'll use to construct the UCCSD ansatz. We have a 4-dimensional Fock
# space, and we know our reference state is the [1, 1, 0, 0] occupation number vector.
space = FermionSpace(4)
state = FermionState([1, 1, 0, 0])

# In order to run a quantum experiment we must express our Hamiltonian as a qubit operator, to do that we use the
# Jordan-Wigner mapping.
jw = QubitMappingJordanWigner()
hermitian_operator = jw.operator_map(hamiltonian_operator)

# Now we can instantiate our ansatz easily by creating the object below. The circuit is generated at instantiation and
# can be accessed through the ansatz.state_circuit attribute.
ansatz = FermionSpaceAnsatzUCCSD(space, state, jw)
print(ansatz.state_circuit)

# We can also get a crude estimate of the quantum resources necessary to implement the ansatz state preparation circuit:
print(ansatz.circuit_resources())

# The quantity we wish to minimize is the expectation value of the Hamiltonian, so we can create the appropriate
# computable.
expectation_value = ExpectationValue(ansatz, hermitian_operator)

# To accelerate the VQE we can evaluate analytic gradients, to do this we have a convenience function available from
# the expectation value computable.
gradient_expression = ExpectationValueDerivative(
    ansatz, hermitian_operator, ansatz.free_symbols_ordered()
)

# Since we are doing a state-vector simulation we need to choose a state-vector protocol.
protocol = SparseStatevectorProtocol(AerStateBackend())

# Now we can run our VQE experiment after instantiation and calling the build method.
vqe = (
    AlgorithmVQE(
        objective_expression=expectation_value,
        gradient_expression=gradient_expression,
        minimizer=MinimizerScipy(),
        initial_parameters=ansatz.state_symbols.construct_zeros(),
    )
    .build(
        protocol_objective=protocol,
        protocol_gradient=protocol,
    )
    .run()
)

print("Minimum Energy: {}".format(vqe.generate_report()["final_value"]))

# examine our UCC coefficients
param_report = vqe.generate_report()["final_parameters"]
for i in range(len(param_report)):
    print(param_report[i]["Symbol"], ":", param_report[i]["Value"])
