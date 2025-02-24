r"""Use of Hadamard test derivative for STO-3G H2 expectation value measurement in direct and indirect mode."""

# imports
from sympy import Symbol

from pytket.extensions.qiskit import AerBackend, AerStateBackend

from inquanto.ansatzes import TrotterAnsatz
from inquanto.computables import ExpectationValueDerivative
from inquanto.express import load_h5
from inquanto.operators import QubitOperatorList
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.protocols import HadamardTestDerivative
from inquanto.states import QubitState

from inquanto.core._math import NumberType

# obtain an example system from express
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator
qubit_hamiltonian = hamiltonian.qubit_encode()

# prepare a simple state
exponents = QubitOperatorList.from_string("theta0 + 0.2*theta1 [(1j, Y0 X1 X2 X3)]")
ansatz = TrotterAnsatz(
    exponents,
    QubitState([1, 1, 0, 0]),
)
# generate a dictionary to insert numerics into the state
parameters = ansatz.state_symbols.construct_from_array([-0.111, -0.0555])

# instantiate a statevector protocol to use for evaluation
sv_protocol = SparseStatevectorProtocol(AerStateBackend())

# instantiate an ExpectationValueDerivative computable and use the statevector protocol to measure it


gradient_expression = ExpectationValueDerivative(
    ansatz, qubit_hamiltonian, ansatz.free_symbols_ordered()
)
# evaluate it with respect to the set of free_symbols at the given parameters values
result_sv = gradient_expression.evaluate(sv_protocol.get_evaluator(parameters))
# this is the exact noise free result for the gradient
print("Derivative with respect to parameters")
print("Statevector", result_sv)


# Now we use a shot based protocol to evaluate the derivatives
# direct and indirect options detailed in arXiv:1701.01450.
hadamard_protocol = HadamardTestDerivative(
    AerBackend(), shots_per_circuit=50000, direct=True
)
hadamard_protocol.build_from(parameters, gradient_expression)
hadamard_protocol.compile_circuits()
print("Direct generates ", len(hadamard_protocol.get_circuits()), "circuits")
hadamard_protocol.run(seed=0)
result_shots = gradient_expression.evaluate(hadamard_protocol.get_evaluator())
print(f"HadamardDirect result: {result_shots}")

# ancilla measurement only with direct=False
indirect_hadamard_protocol = HadamardTestDerivative(
    AerBackend(), shots_per_circuit=50000, direct=False
)
diff_symbols = ansatz.state_symbols
indirect_hadamard_protocol.build(
    parameters,
    ansatz,
    qubit_hamiltonian,
    None,
    NumberType.REAL,
).compile_circuits()
print("Indirect generates ", len(indirect_hadamard_protocol.get_circuits()), "circuits")
# asynchronous run
handles = indirect_hadamard_protocol.launch(seed=0)
indirect_hadamard_protocol.retrieve(handles)

# print(indirect_hadamard_protocol._measurement_df)
# print(indirect_hadamard_protocol._circuit_df)

# evaluation without computable
value = indirect_hadamard_protocol.evaluate_gradient(
    ansatz, qubit_hamiltonian, {Symbol("theta0"), Symbol("theta1")}
)
print(f"Indirect HadamardDirect result: {value}")
