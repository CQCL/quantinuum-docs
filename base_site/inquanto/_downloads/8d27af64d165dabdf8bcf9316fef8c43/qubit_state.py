r"""Construction of QubitState and demonstration of some functionality."""

# imports
from sympy import Symbol

from inquanto.states import QubitState, QubitStateString

# constructing qubit states and qubit state strings
qs0 = QubitState([1, 1, 0, 0], 1)
qs_orth = QubitState([0, 0, 1, 1], 1)

# equivalently to qs0 QubitStates can be made from QubitStateStrings
qss = QubitStateString([1, 1, 0, 0])
qs1 = QubitState(qss, 1)


# a qubit state can be prepared as a linear combination of
# basis states
qss0 = QubitStateString([1, 1, 0, 0])
qss1 = QubitStateString([1, 0, 1, 0])
qs2 = QubitState(((0.9, qss0), (0.1, qss1)))

qs3 = QubitState({qss0: 0.9, qss1: 0.1})
print("Are qs2 and qs3 equal? ", qs3 == qs2)
print("Is qs3 a basis state? ", qs3.is_basis_state())
print("What are qs3's basis states?")
print(qs3.basis_states)
print("Is qs3 normalized? ", qs3.is_normalized())
# we can normalize the coefficients with qs3.normalized()
print("")

# dotting qubit states
# dot with self is 1
print("self dot:", qs0.vdot(qs1))

# dot with ortho vector is 0
print("dot with orthogonal state: ", qs0.vdot(qs_orth))

# get state as a list
print(qs0.single_term)
# this will fail for qs3, which is a linear combination of states

# get the number of qubits in the state space
print("Number of qubits:", qs0.num_qubits)
print("")

# coefficients of qubit states can be symbolic
sym_coeff = Symbol("a_1")
sym_coeff2 = Symbol("b_1")
qs_dict = QubitState({qss0: sym_coeff2, qss1: sym_coeff})
print("Free symbols before substitution", qs_dict.free_symbols())

# note: can't normalize symbolic states
simple_sd = dict({sym_coeff: 1.1, sym_coeff2: 0.1})

# insert numeric values into symbolic state
qs_dict.symbol_substitution(simple_sd)
print("Free symbols after substitution", qs_dict.free_symbols())
# we can renormalize our numeric state coefficients
qs_dict = qs_dict.normalized()
print("Normalized QS table")
qs_dict.print_table()
