r"""Use of symbolic protocol for expectation value."""

# imports
from sympy import Symbol
from inquanto.computables import ExpectationValue
from inquanto.ansatzes import TrotterAnsatz
from inquanto.express import load_h5
from inquanto.operators import QubitOperatorList
from inquanto.protocols import SymbolicProtocol
from inquanto.states import QubitState

# load system from express
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
qubit_hamiltonian = h2.hamiltonian_operator.qubit_encode()

# construct small ansatz
exponents = QubitOperatorList.from_string("theta [(1j, Y0 X1 X2 X3)]")
reference = QubitState([1, 1, 0, 0])
ansatz = TrotterAnsatz(exponents, reference)

parameters = {Symbol("theta"): -0.111}

# define a quantum computable quantity
energy = ExpectationValue(ansatz, qubit_hamiltonian)

# instantiate a symbolic protocol to use as an evaluator of the exp val
protocol = SymbolicProtocol()
# symbolic evaluation generates a functional form of the circuit and then inserts
# numerics for evaluation after
energy_value = energy.evaluate(evaluator=protocol.get_evaluator(parameters))
print(f"Energy value: {energy_value}")
# -1.1368226230074179
