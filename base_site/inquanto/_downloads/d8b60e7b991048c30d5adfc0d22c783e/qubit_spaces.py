r"""Use of QubitSpace object to generate qubit operators."""

# imports
import numpy as np

from inquanto.operators import QubitOperator
from inquanto.spaces import QubitSpace
from inquanto.states import QubitState

# create a qubit space for N qubits (N=4 here)
space = QubitSpace(4)
state = QubitState([1, 1, 0, 0])

# can use spaces to build QubitOperators of specific types
real_exp = space.construct_real_pauli_exponent_operators()
imag_exp = space.construct_imag_pauli_exponent_operators()
pauli_exps = real_exp + imag_exp
print("number of pauli exponent operators of type in space:", len(pauli_exps))

example_operator = QubitOperator("X0 X1 X2 X3")
print(space.symmetry_operators_z2(example_operator))
print(space.symmetry_operators_z2_in_sector(example_operator, state))

# further detailed examples in examples/symmetry
