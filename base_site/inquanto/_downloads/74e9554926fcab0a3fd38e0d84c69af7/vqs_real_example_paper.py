r"""A AlgorithmMcLachlanRealTime time evolution simulation for a small system."""

# contrast to vqs_real_example_paper_phased https://doi.org/10.22331/q-2019-10-07-191

# imports
import numpy

from pytket.extensions.qiskit import AerStateBackend

from sympy import Symbol

from inquanto.algorithms.time_evolution import (
    AlgorithmMcLachlanRealTime,
)
from inquanto.ansatzes import CircuitAnsatz, TrotterAnsatz
from inquanto.computables.atomic import ExpectationValue
from inquanto.minimizers._solver_euler import NaiveEulerIntegrator
from inquanto.operators import QubitOperatorList, QubitOperator
from inquanto.protocols import (
    SparseStatevectorProtocol,
)


def plotting(time_span, evs, solution, symbols, name, title):
    from matplotlib import pyplot as plt

    fig = plt.figure(figsize=(4, 4))

    # (ax0, ax1, ax2, ax3) = fig.subplots(4, 1)
    (ax0, ax1) = fig.subplots(2, 1)

    fig.suptitle(f"{title}\n{name}")
    ax0.plot(time_span, solution, label=symbols)
    # ax1.plot(time_span, evs[:, 2:], label="occupation")
    ax1.plot(time_span, evs[:], label="energy")
    # ax3.plot(time_span, evs[:, 1], label="total particle")

    ax0.legend()

    ax0.set_ylabel(r"Ansatz parameters")
    # ax1.set_ylabel("Occupation number\n(spin orbital)")
    # ax2.set_ylabel(r"Total energy ($Ha$)")
    ax1.set_ylabel(r"Total energy ($Ha$)")
    # ax3.set_ylabel(r"Total number of particle")
    # ax3.set_xlabel(r"time ($\hbar/Ha$)")
    ax1.set_xlabel(r"time ($\hbar/Ha$)")

    fig.tight_layout()
    fig.savefig(f"figure_{title}_{name}.png")

    plt.show()


# Construct toy model from https://doi.org/10.22331/q-2019-10-07-191
c = TrotterAnsatz(
    QubitOperatorList.from_string("theta0 [(1j, X0)], theta1 [(1j, Z0)]")
).get_circuit()
c.add_phase(Symbol("phi0"))
ansatz = CircuitAnsatz(c)

hamiltonian = QubitOperator.from_string("(1.0, Y0)")

initial = ansatz.state_symbols.construct_from_array([0.0, 0.1734, 0.3909])

print(initial)
time = numpy.linspace(0, 10, 1001)
integrator = NaiveEulerIntegrator(
    time, disp=True, linear_solver=NaiveEulerIntegrator.linear_solver_scipy_pinvh
)

# use specific time evolution class
algodeint = AlgorithmMcLachlanRealTime(
    integrator,
    hamiltonian,
    ansatz,
    initial_parameters=initial,
)

protocol = SparseStatevectorProtocol(AerStateBackend())

solution = algodeint.build(
    protocol=protocol,
).run()


# After the evolution run, we can measure/evaluate quantities at eacth time step:
evs_exp_runner = protocol.get_runner(ExpectationValue(ansatz, hamiltonian))

evs = algodeint.post_propagation_evaluation(evs_exp_runner)
evs = numpy.asarray(evs)

plotting(
    time,
    evs,
    solution,
    ansatz.state_symbols,
    "AlgorithmMcLachlanRealTime",
    "Y0papereq12",
)
