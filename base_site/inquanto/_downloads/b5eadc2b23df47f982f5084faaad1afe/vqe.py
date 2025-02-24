r"""Example of running VQE with a UCCD ansatz using the CuTensorNetBackend."""

from inquanto.algorithms import AlgorithmVQE
from inquanto.ansatzes import FermionSpaceAnsatzUCCD
from inquanto.computables import ExpectationValue, ExpectationValueDerivative
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import MinimizerScipy
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState
from pytket.extensions.cutensornet import CuTensorNetStateBackend
from pytket.extensions.qiskit import AerStateBackend

from inquanto.extensions.cutensornet import CuTensorNetProtocol

h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator
qubit_hamiltonian = hamiltonian.qubit_encode()
space = FermionSpace(4)
state = FermionState([1, 1, 0, 0])
ansatz = FermionSpaceAnsatzUCCD(space, state, QubitMappingJordanWigner())

expectation_value = ExpectationValue(ansatz, qubit_hamiltonian)
gradient_expression = ExpectationValueDerivative(
    ansatz, qubit_hamiltonian, ansatz.free_symbols_ordered()
)

# Use the native tensornetwork operations
protocol_tn = CuTensorNetProtocol()
vqe_tn = (
    AlgorithmVQE(
        objective_expression=expectation_value,
        gradient_expression=gradient_expression,
        minimizer=MinimizerScipy(),
        initial_parameters=ansatz.state_symbols.construct_zeros(),
    )
    .build(protocol_objective=protocol_tn, protocol_gradient=protocol_tn)
    .run()
)
print(vqe_tn.generate_report()["final_value"])

# Use the tensornetwork backend to do a statevector simulation
protocol_tn = SparseStatevectorProtocol(CuTensorNetStateBackend())
vqe_sv = (
    AlgorithmVQE(
        objective_expression=expectation_value,
        gradient_expression=gradient_expression,
        minimizer=MinimizerScipy(),
        initial_parameters=ansatz.state_symbols.construct_zeros(),
    )
    .build(protocol_objective=protocol_tn, protocol_gradient=protocol_tn)
    .run()
)
print(vqe_sv.generate_report()["final_value"])

# The native tensornetwork operations may be slower for this small example, but
# they are more scalable on the appropriate GPU hardware.
