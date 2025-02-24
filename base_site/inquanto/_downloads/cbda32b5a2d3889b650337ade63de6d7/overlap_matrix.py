r"""Simple overlap matrix calculation."""

# imports
from sympy import Symbol

from inquanto.computables.composite import (
    OverlapMatrixComputable,
)
from inquanto.express import ansatzYXXX

theta = Symbol("theta")
# prepare two instances a simple ansatz with different parameters
state1 = ansatzYXXX.subs({theta: 0.2})
state2 = ansatzYXXX.subs({theta: 0.8})

print("States:")
print(state1.df_numeric())
print(state2.df_numeric())

# evaluates S_{ij} = <\Psi_i|\hat{O}|\Psi_j>
overlap = OverlapMatrixComputable([state1, state2])

# use the default statevector evaluation
s = overlap.default_evaluate({})

# examine the matrix
print(s)
