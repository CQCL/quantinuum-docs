r"""Basic CI calculation with NonOrthogonal computable."""

# imports
import math
from sympy import Symbol

from inquanto.ansatzes import MultiConfigurationState
from inquanto.computables.composite import (
    NonOrthogonalMatricesComputable,
)
from inquanto.core import pd_safe_eigh
from inquanto.express import load_h5, ansatzYXXX
from inquanto.states import QubitState

# load example system from express
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
qubit_hamiltonian = h2.hamiltonian_operator.qubit_encode()

# Let's try first simple CI states:
print("=== Using orthogonal states ===")
# note fixed coefficients
state1 = MultiConfigurationState(QubitState([1, 1, 0, 0]))
state2 = MultiConfigurationState(QubitState([0, 0, 1, 1]))

print("States:")
print(state1.df_numeric())
print(state2.df_numeric())

# evaluates H and S in HC = eSC in the basis of the given list of states
noc12 = NonOrthogonalMatricesComputable(qubit_hamiltonian, [state1, state2])

# evaluate the matrices using statevector protocol
h, s = noc12.default_evaluate({})

# use matrices to solve HC = eSC
ev, ew, _ = pd_safe_eigh(h, s)

# compare to stored FCI energy in express
print("CASCI ENERGY: ", h2.energy_casci)
print("NO METHOD CI: ", ev[0])
print("")


# Now, let's try non-orthogonal states:
print("=== Using non-orthogonal states ===")
theta = Symbol("theta")
state3 = ansatzYXXX.subs({theta: 0.2})
state4 = ansatzYXXX.subs({theta: 0.8})

print("States:")
print(state3.df_numeric())
print(state4.df_numeric())

noc34 = NonOrthogonalMatricesComputable(qubit_hamiltonian, [state3, state4])

h, s = noc34.default_evaluate({})

ev, ew, _ = pd_safe_eigh(h, s)

print("CASCI ENERGY: ", h2.energy_casci)
print("NO METHOD CI: ", ev[0])
print("")


print("=== Using other non-orthogonal states ===")
state5 = MultiConfigurationState(
    QubitState([1, 1, 0, 0], math.sqrt(0.25))
    + QubitState([0, 0, 1, 1], math.sqrt(0.75))
)
state6 = MultiConfigurationState(
    QubitState([1, 1, 0, 0], math.sqrt(0.6)) + QubitState([0, 0, 1, 1], math.sqrt(0.4))
)

print("States:")
print(state5.df_numeric())
print(state6.df_numeric())

noc56 = NonOrthogonalMatricesComputable(qubit_hamiltonian, [state5, state6])

h, s = noc56.default_evaluate({})

ev, ew, _ = pd_safe_eigh(h, s)

print("CASCI ENERGY: ", h2.energy_casci)
print("NO METHOD CI: ", ev[0])

# all secular equations yield the FCI energy through different mixtures of the
# two differently weighted qubit states.
