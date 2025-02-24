r"""Demonstrates the general use of computables and protocols."""

# imports
from pytket.extensions.qiskit import AerBackend, AerStateBackend
from pytket.partition import PauliPartitionStrat

from inquanto.ansatzes import TrotterAnsatz
from inquanto.express import load_h5
from inquanto.operators import QubitOperatorList
from inquanto.states import QubitState
from inquanto.computables import ExpectationValue
from inquanto.computables.primitive import ComputableFunction

# load an example system from express
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
qubit_hamiltonian = h2.hamiltonian_operator.qubit_encode()

# prepare a minimal ansatz circuit
exponents = QubitOperatorList.from_string("theta [(1j, Y0 X1 X2 X3)]")
reference = QubitState([1, 1, 0, 0])
ansatz = TrotterAnsatz(exponents, reference)
parameters = parameters = {"theta": -0.41}

# construct a Computable which reports the variance
qc_variance = ComputableFunction(
    lambda x, y: x - y,
    ExpectationValue(ansatz, qubit_hamiltonian**2),
    ComputableFunction(lambda x: x**2, ExpectationValue(ansatz, qubit_hamiltonian)),
)

print(
    "Variance with default statevector: "
    + str(qc_variance.default_evaluate(parameters))
)

# construct a manual evaluator
# this uses explicit state algebra to yield the expectation value
def my_evaluator(qc):
    if isinstance(qc, ExpectationValue):
        v = qc.state.get_numeric_representation(parameters)
        return qc.kernel.state_expectation(v).real
    return qc


print(
    "Variance with manual statevector: "
    + str(qc_variance.evaluate(evaluator=my_evaluator))
)

##
from inquanto.protocols import SparseStatevectorProtocol

sv = SparseStatevectorProtocol(AerStateBackend())
sv_evaluator = sv.get_evaluator(parameters)
print(
    "Variance with explicit pytket backend statevector: "
    + str(qc_variance.evaluate(evaluator=sv_evaluator))
)

# shot based evaluation
from inquanto.protocols import PauliAveraging

# Instantiate a protocol for evaluating exp vals using pauli averaging
# we choose to use 1000 shots
pa = PauliAveraging(
    AerBackend(),
    shots_per_circuit=1000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)

# build circuits
pa.build_from(parameters, qc_variance).compile_circuits()
# run circuits and collect results
pa.run(seed=0)

## use stored PA results to inform the computable evaluation
pa_evaluator = pa.get_evaluator()
print(
    "Variance with explicit shot based protocol: "
    + str(qc_variance.evaluate(evaluator=pa_evaluator))
)


# alternative synchronous flow using runners
sv_runner_variance = sv.get_runner(qc_variance)
print("Variance with statevector runner: " + str(sv_runner_variance(parameters)))

pa_runner_variance = pa.get_runner(qc_variance)
print("Variance with PA runner: " + str(pa_runner_variance(parameters)))
