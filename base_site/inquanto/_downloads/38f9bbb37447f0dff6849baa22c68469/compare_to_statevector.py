r"""Comparison between statevector and tensor network protocols."""

from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.computables import ExpectationValue, MetricTensorReal, Overlap
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.operators import QubitOperator
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState
from pytket.extensions.qiskit import AerStateBackend

from inquanto.extensions.cutensornet import CuTensorNetProtocol

h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator
qubit_hamiltonian = hamiltonian.qubit_encode()
space = FermionSpace(4)
state = FermionState([1, 1, 0, 0])
ansatz = FermionSpaceAnsatzUCCSD(space, state, QubitMappingJordanWigner())
parameters = ansatz.state_symbols.construct_random()

sv_protocol = SparseStatevectorProtocol(AerStateBackend())
tn_protocol = CuTensorNetProtocol()

# Expectation values
expression = ExpectationValue(ansatz, qubit_hamiltonian)
sv = expression.evaluate(sv_protocol.get_evaluator(parameters))
tn = expression.evaluate(tn_protocol.get_evaluator(parameters))
print("ExpectationValue")
print(sv)
print(tn)

# Overlap
expression = Overlap(ansatz, ansatz)
sv = expression.evaluate(sv_protocol.get_evaluator(parameters))
tn = expression.evaluate(tn_protocol.get_evaluator(parameters))
print("Overlap")
print(sv)
print(tn)

# Metric tensor
expression = MetricTensorReal(ansatz, [ansatz.state_symbols.symbols[0]])
sv = expression.evaluate(sv_protocol.get_evaluator(parameters))
tn = expression.evaluate(tn_protocol.get_evaluator(parameters))
print("MetricTensorReal")
print(sv)
print(tn)
