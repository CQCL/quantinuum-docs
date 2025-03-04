r"""A custom equation of motion VQS time evolution simulation."""
# contrast to vqs_real_example_paper https://doi.org/10.22331/q-2019-10-07-191

# imports
import numpy
from pytket import Circuit
from pytket.extensions.qiskit import AerStateBackend

from inquanto.algorithms.time_evolution import (
    AlgorithmVQS,
)
from inquanto.ansatzes import TrotterAnsatz
from inquanto.computables.atomic import (
    ExpectationValue,
    MetricTensorReal,
    ExpectationValueBraDerivativeImag,
    ExpectationValueBraDerivativeReal,
)
from inquanto.computables.primitive import ComputableFunction, ComputableTuple
from inquanto.core._dict_to_arrays import (
    dict_to_vector,
    dict_to_matrix,
)
from inquanto.minimizers._solver_euler import NaiveEulerIntegrator
from inquanto.operators import QubitOperatorList, QubitOperator
from inquanto.protocols import (
    SparseStatevectorProtocol,
)

# We define a plotting function for the energy and orbital occupation numbers of the system
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
ansatz = TrotterAnsatz(
    QubitOperatorList.from_string("theta0 [(1j, X0)], theta1 [(1j, Z0)]"),
    Circuit(1).add_phase(1 / 3),
)

hamiltonian = QubitOperator.from_string("(1.0, Y0)")

initial = ansatz.state_symbols.construct_from_array([0.1734, 0.3909])

time = numpy.linspace(0, 10, 1001)
integrator = NaiveEulerIntegrator(time, disp=True)

# Build custom EOM computable
symbols = ansatz.state_symbols.symbols

# Custom equation of motion equation.
# Should give better energy conservation than general class for this state.
def evaluate_eom(eom_terms):
    matrix = dict_to_matrix(symbols, eom_terms[0])
    vector = dict_to_vector(symbols, eom_terms[1])
    energy = eom_terms[2]
    dbra_ovl_re = dict_to_vector(symbols, eom_terms[3])
    dbra_ovl_im = dict_to_vector(symbols, eom_terms[4])
    mat = numpy.zeros_like(matrix, dtype=complex)
    vec = numpy.zeros_like(vector, dtype=complex)
    for i in range(vector.size):
        for j in range(vector.size):
            mat[i, j] = matrix[i, j] + (dbra_ovl_re[i] + 1j * dbra_ovl_im[i]) * (
                dbra_ovl_re[j] + 1j * dbra_ovl_im[j]
            )
        vec[i] = 1 * vector[i] + 1j * (dbra_ovl_re[i] + 1j * dbra_ovl_im[i]) * energy

    return mat.real, vec.real


identity = QubitOperator.identity()
custom_eom = ComputableFunction(
    evaluate_eom,
    ComputableTuple(
        MetricTensorReal(ansatz, symbols),
        ExpectationValueBraDerivativeImag(ansatz, hamiltonian, symbols),
        ExpectationValue(ansatz, hamiltonian),
        ExpectationValueBraDerivativeReal(ansatz, identity, symbols),
        ExpectationValueBraDerivativeImag(ansatz, identity, symbols),
    ),
)

# Plug the custom equation of motion computable into the generic time evolution class
algodeint = AlgorithmVQS(
    integrator,
    custom_eom,
    initial_parameters=initial,
)

protocol = SparseStatevectorProtocol(AerStateBackend())

solution = algodeint.build(
    protocol=protocol,
).run()


# After the evolution run, we can measure/evaluate quantities at each time step:
evs_exp_runner = protocol.get_runner(ExpectationValue(ansatz, hamiltonian))

evs = algodeint.post_propagation_evaluation(evs_exp_runner)
evs = numpy.asarray(evs)

plotting(
    time,
    evs,
    solution,
    ansatz.state_symbols,
    "AlgorithmVQSCustom",
    "Y0papereq35",
)
