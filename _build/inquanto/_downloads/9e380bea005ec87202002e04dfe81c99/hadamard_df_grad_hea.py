r"""Use of Hadamard test derivative for STO-3G H2 expectation value measurement with a hardware-efficient ansatz."""
from sympy import Symbol

from pytket.extensions.qiskit import AerBackend, AerStateBackend
from pytket.circuit import OpType
from pytket.partition import PauliPartitionStrat

from inquanto.ansatzes import HardwareEfficientAnsatz

from inquanto.computables import ExpectationValue, ExpectationValueDerivative

from inquanto.express import load_h5

from inquanto.protocols import SparseStatevectorProtocol, HadamardTestDerivative
from inquanto.states import QubitState


# H2 STO-3G Hamiltonian
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator

qubit_hamiltonian = hamiltonian.qubit_encode()

ansatz = HardwareEfficientAnsatz([OpType.Ry], QubitState([1, 1, 0, 0]), 1)

parameters = ansatz.state_symbols.construct_random()

# Reference SV values
energy = ExpectationValue(ansatz, qubit_hamiltonian)
gradient_expression = ExpectationValueDerivative(
    ansatz, qubit_hamiltonian, ansatz.free_symbols_ordered()
)
result_sv = gradient_expression.evaluate(
    SparseStatevectorProtocol(AerStateBackend()).get_evaluator(parameters)
)

# shot based
protocol = HadamardTestDerivative(
    AerBackend(),
    shots_per_circuit=50000,
)

symbols = {Symbol("c0a0"), Symbol("l0b0a0"), Symbol("l0b0a3")}

protocol.build(parameters, ansatz, qubit_hamiltonian, None, component="real")
protocol.compile_circuits()

handles = protocol.launch(seed=0)
protocol.retrieve(handles)

print(protocol._measurement_df)
print(protocol._circuit_df)

value = protocol.evaluate_gradient(ansatz, qubit_hamiltonian, None)

print(f"Parameters list: {parameters}")
print(f"SV result: {result_sv}")
print(f"HadamardTestDerivative result: {value}")
