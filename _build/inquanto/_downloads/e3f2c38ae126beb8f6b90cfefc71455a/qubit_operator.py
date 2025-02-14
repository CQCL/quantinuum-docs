r"""Construction of QubitOperator and demonstration of some functionality."""

# imports
from sympy import sympify

from pytket.circuit import Pauli

from inquanto.operators import QubitOperator, QubitOperatorList, QubitOperatorString
from inquanto.states import QubitState

# constructing qubit operators
# same QO by three methods
op0 = QubitOperator("X0 Y2 Z3", 4.6)
op1 = QubitOperator(((0, "X"), (1, "Y"), (3, "Z")), 4.6)
op2 = QubitOperator([(0, "X"), (1, "Y"), (3, "Z")], 4.6)
qs = QubitOperatorString.from_string("X0 Y1 Z3")
op3 = QubitOperator(qs, 4.6)

# qubit operator actions
print("initial operator:", op3)
print("dagger:", op3.dagger())  # take adjoint of operator
print("mult:", op3 * op3)  # multiply two operators
print("commutator with op0:", op3.commutator(op0))  # construct commutator
print("check if operators commute:", op3.commutes_with(op0))

# prepare a qubit state to act with these operators on
qubit_state = QubitState([1, 1, 0, 0], 1)

# act with qubit operator on qubit state
print("act on state:", op3.dot_state(qubit_state))

# get expectation value of operator wrt state
print("get expectation value:", op3.state_expectation(qubit_state))
print("")


# These operators coefficients can be made symbolic and held in a
# qubit operator list (QOL)
a, b, c = sympify("a,b,c")
qol = QubitOperatorList([(a**3, op1), (2, op3), (b, op2), (c, op3)])

print("reversed operator list:")
print(qol.reversed_order())
print("")

print("jacobian as row-sorted list:")
jacobian = qol.compute_jacobian([a, b])
print(jacobian)


qs0 = QubitOperatorString.from_string("X0 Y1 Z3")
qs1 = QubitOperatorString.from_tuple([(0, Pauli.Y), (1, Pauli.X)])

# get a list of the qubits acted upon by the qubit operator string
print("qubits in operator:")
print(qs0.qubit_id_list)

# get a list of gates present in the string
print("gates in operator")
print(qs0.pauli_list)
print("")


# constructing a sum of qubit operator strings
dictionary = {qs0: 4.6, qs1: -1.7j}
op4 = QubitOperator(dictionary)
print("op4, with a sum of qubit operators", op4)

# trotterize an operator, creates a QOL
op4_trot = op4.trotterize(trotter_number=1, trotter_order=1)
print("op4 trotterized:", op4_trot)
print(type(op4_trot))
