r"""Use of Hadamard test derivative for STO-3G H2 expectation value measurement."""
# Computable expression example (ExpectationValue):
# A general way to convert familiar quantum chemistry expressions to measurement circuits.
from sympy import Symbol

from pytket.partition import PauliPartitionStrat
from pytket.extensions.qiskit import AerBackend, AerStateBackend

from inquanto.ansatzes import TrotterAnsatz

from inquanto.computables import ExpectationValue, ExpectationValueDerivative

# H2 STO-3G Hamiltonian
from inquanto.express import load_h5

from inquanto.operators import QubitOperatorList
from inquanto.protocols import SparseStatevectorProtocol, HadamardTestDerivative
from inquanto.states import QubitState


h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator

qubit_hamiltonian = hamiltonian.qubit_encode()

exponents = QubitOperatorList.from_string("theta0 + 0.2*theta1 [(1j, Y0 X1 X2 X3)]")

ansatz = TrotterAnsatz(
    exponents,
    QubitState([1, 1, 0, 0]),
)


parameters = ansatz.state_symbols.construct_from_array([-0.111, -0.0555])

# Reference SV values
energy = ExpectationValue(ansatz, qubit_hamiltonian)
gradient_expression = ExpectationValueDerivative(
    ansatz, qubit_hamiltonian, ansatz.free_symbols_ordered()
)
result_sv = gradient_expression.evaluate(
    SparseStatevectorProtocol(AerStateBackend()).get_evaluator(parameters)
)

# shot based protocol
protocol = HadamardTestDerivative(
    AerBackend(),
    shots_per_circuit=50000,
)

protocol.build(
    parameters,
    ansatz,
    qubit_hamiltonian,
    {Symbol("theta0"), Symbol("theta1")},
    component="real",
).compile_circuits()

handles = protocol.launch(seed=0)
protocol.retrieve(handles)

print(protocol._measurement_df)
print(protocol._circuit_df)

value = protocol.evaluate_gradient(
    ansatz, qubit_hamiltonian, {Symbol("theta0"), Symbol("theta1")}
)

print(f"SV result: {result_sv}")
print(f"HadamardTestDerivative result: {value}")
