r"""Symbolic evaluation and comparing integrator methods."""

# imports
import numpy as np

from sympy import Symbol, Array

from inquanto.ansatzes import CircuitAnsatz, TrotterAnsatz
from inquanto.minimizers import (
    NaiveEulerIntegrator,
    ScipyIVPIntegrator,
    ScipyODEIntegrator,
)
from inquanto.operators import QubitOperatorList, QubitOperator
from inquanto.computables.atomic import (
    ExpectationValueBraDerivativeImag,
    MetricTensorReal,
    ExpectationValue,
)
from inquanto.computables.primitive import ComputableTuple
from inquanto.protocols import SymbolicProtocol
from inquanto.core import dict_to_vector, dict_to_matrix


# prepare a simple ansatz state with 2 parameterized operators
c = TrotterAnsatz(
    QubitOperatorList.from_string("theta0 [(1j, X0)], theta1 [(1j, Z0)]")
).get_circuit()
# add a global phase parameter
c.add_phase(Symbol("phi0"))
# create ansatz class from circuit
ansatz = CircuitAnsatz(c)
# the ansatz has 3 free symbols
print("Free symbols")
print(ansatz.free_symbols())

hamiltonian = QubitOperator.from_string("(1.0, Y0)")
# make an initial dictionary to define initial state
initial = ansatz.state_symbols.construct_from_array([0.0, 0.1734, 0.3909])


print("# PREPARE SYMBOLIC EVALUATIONS...")


# yield vector b of linear problem for our time evolution
ci = ExpectationValueBraDerivativeImag(ansatz, hamiltonian, ansatz.state_symbols)

# yield matrix A of linear problem for our time evolution
ar = MetricTensorReal(ansatz, ansatz.state_symbols)

# use protocol to obtain runner for the computable
# this symbolic protocol could be replaced with Statevector
# or another appropriate class for evaluation
runner = SymbolicProtocol().get_runner(ComputableTuple(ci, ar))

# alternative
# from inquanto.protocols import SparseStatevectorProtocol
# from pytket.extensions.qiskit import AerStateBackend
# runner = SparseStatevectorProtocol(AerStateBackend()).get_runner(ComputableTuple(ci, ar))

print("# RUN TIME EVOLUTIONS...")

# define a method which takes parameters and the time step and returns
# the linear problem (matrix A(t), vector b(t) of A*x=b) at a time


def linear_problem(p, t):
    # prepare a symbol dict with the given symbols
    m = ansatz.state_symbols.construct_from_array(p)
    # run the Symbolic protocols for evaluating ExpectationValueBraDerivativeImag
    # and MetricTensor with respect to the symbols.
    grad_dict, mt_dict = runner(m)

    # use express methods to reformat the results for the integrator
    return dict_to_matrix(ansatz.state_symbols, mt_dict), dict_to_vector(
        ansatz.state_symbols, grad_dict
    )


# prepare range of time-evolution
time = np.linspace(0, 0.5, 51)


print("# EULER INTEGRATOR...")
# instance the integrator class with the time range
euler = NaiveEulerIntegrator(time, disp=True)
# perform integration of the linear problem starting from the initial state
solution_euler = euler.solve(linear_problem, [0.0, 0.1734, 0.3909])
print("")

print("# ScipyIVP INTEGRATOR...")
ivp = ScipyIVPIntegrator(time, disp=True)
solution_ivp = ivp.solve(linear_problem, [0.0, 0.1734, 0.3909])
print("")

print("# ScipyODE INTEGRATOR...")
odeint = ScipyODEIntegrator(time, disp=True)
solution_odeint = odeint.solve(linear_problem, [0.0, 0.1734, 0.3909])
print("")


# go over the stored symbols from each step of time evolution and use them to
# evaluate the system energy for each integrator
energies_euler = [
    ExpectationValue(ansatz, hamiltonian).default_evaluate(
        ansatz.state_symbols.construct_from_array(p)
    )
    for p in solution_euler
]
energies_ivp = [
    ExpectationValue(ansatz, hamiltonian).default_evaluate(
        ansatz.state_symbols.construct_from_array(p)
    )
    for p in solution_ivp
]
energies_odeint = [
    ExpectationValue(ansatz, hamiltonian).default_evaluate(
        ansatz.state_symbols.construct_from_array(p)
    )
    for p in solution_odeint
]


# Plot the results
from matplotlib import pyplot as plt

fig = plt.figure(figsize=(4, 8))

(ax0, ax1, ax2, ax3) = fig.subplots(4, 1)

fig.suptitle(f"Integrators")
ax0.plot(time, solution_euler, label=ansatz.state_symbols.symbols)
ax1.plot(time, solution_ivp, label=ansatz.state_symbols.symbols)
ax2.plot(time, solution_odeint, label=ansatz.state_symbols.symbols)
ax3.plot(time, energies_euler, label="Euler")
ax3.plot(time, energies_ivp, label="IVP")
ax3.plot(time, energies_odeint, label="ODEINT")

ax0.legend()
ax3.legend()

ax0.set_ylabel(r"parameters (Euler)")
ax1.set_ylabel(r"parameters (IVP)")
ax2.set_ylabel(r"parameters (ODEINT)")
ax3.set_ylabel(r"Total energy ($Ha$)")
ax3.set_xlabel(r"time ($\hbar/Ha$)")

fig.tight_layout()
fig.savefig(f"figure_integrators.png")

plt.show()
