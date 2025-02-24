r"""An example showing how to use evaluate gradients and compare against finite differences"""

# imports
from sympy import Symbol

from pytket.extensions.qiskit import AerBackend, AerStateBackend

from inquanto.ansatzes import TrotterAnsatz
from inquanto.express import load_h5
from inquanto.operators import QubitOperatorList
from inquanto.states import QubitState
from inquanto.computables.primitive import ComputableTuple, ComputableFunction
from inquanto.computables import (
    Overlap,
    ExpectationValue,
    ExpectationValueDerivative,
    ExpectationValueBraDerivativeImag,
    ExpectationValueBraDerivativeReal,
)
from inquanto.protocols import SparseStatevectorProtocol

backend = AerStateBackend()

# load operator from express
op1 = load_h5("h2_sto3g.h5", as_tuple=True).hamiltonian_operator.qubit_encode()
exponents = QubitOperatorList.from_string("theta [(1j, Y0 X1 X2 X3)]")


# prepare ansatz with symbols that we will create a finite difference
# between +/-delta
delta = Symbol("delta")
theta = Symbol("theta")

# set the value gap between the two states
delta_value = 1e-6

symbol_dict = {theta: 0.3, delta: delta_value}

ref = QubitState([1, 1, 0, 0])

# create the ansatz state, and the + and - finite diff states
state = TrotterAnsatz(exponents, ref)
state1p = state.subs({theta: theta + delta})
state1m = state.subs({theta: theta - delta})

# finite difference definition function
fd = lambda fp, fm: (fp - fm) / 2 / delta_value

# create computable functions which return finite difference functions
c1gfd = ComputableFunction(
    fd, ExpectationValue(state1p, op1), ExpectationValue(state1m, op1)
)
c1brafd = ComputableFunction(
    fd, Overlap(state1p, state, op1), Overlap(state1m, state, op1)
)
c1ketfd = ComputableFunction(
    fd, Overlap(state, state1p, op1), Overlap(state, state1m, op1)
)

# for comparison we make computables for analytical derivatives
c1g = ExpectationValueDerivative(state, op1, state.free_symbols())
c1i = ExpectationValueBraDerivativeImag(state, op1, state.free_symbols())
c1r = ExpectationValueBraDerivativeReal(state, op1, state.free_symbols())

ce = ComputableTuple(c1gfd, c1g, c1r, c1i, c1brafd, c1ketfd)

runner = SparseStatevectorProtocol(backend).get_runner(ce)

# we run all the protocols for our various computables and collect results
c1gfd_ev, c1g_ev, c1r_ev, c1i_ev, c1brafd_ev, c1ketfd_ev = runner(symbol_dict)

# finite difference
print("Finite difference:")
print("       (<Psi(t+h)|H|Psi(t+h)> - <Psi(t-h)|H|Psi(t-h)>)/(2h)  :", c1gfd_ev)
# analytical
print("Analytical:")
print("       (<Psi(t)|H|Psi(t)> (ExpectationValueDerivative)     :", c1g_ev)
# finite difference bra

print("DBra = (<Psi(t+h)|H|Psi(t)> - <Psi(t-h)|H|Psi(t)>)/(2h)      :", c1brafd_ev)
# finite difference ket
print("DKet = (<Psi(t)|H|Psi(t+h)> - <Psi(t)|H|Psi(t-h)>)/(2h)      :", c1ketfd_ev)

print(
    "       DBra + DKet                                           :",
    c1ketfd_ev + c1brafd_ev,
)
print("")
# compare below to finite difference bra
print("Analytical:")
print("Re (<DPsi(t)|H|Psi(t)> (ExpectationValueBraDerivativeImag) :", c1r_ev)
# For this set up the imaginary component is very small so there may be large
# fluctuations due to stochasticity
print("Im (<DPsi(t)|H|Psi(t)> (ExpectationValueBraDerivativeImag) :", c1i_ev)
