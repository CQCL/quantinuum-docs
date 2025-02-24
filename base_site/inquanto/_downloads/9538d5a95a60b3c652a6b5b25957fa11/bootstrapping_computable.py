r"""Computable level usage of BackendResult resampling classes for bootstrapping of H2 energy (STO-3G)."""
from pytket.extensions.qiskit import AerBackend

from inquanto.ansatzes import TrotterAnsatz
from inquanto.computables import ExpectationValue

# H2 STO-3G Hamiltonian
from inquanto.express import load_h5
from inquanto.operators import QubitOperator, QubitOperatorList
from inquanto.protocols import PauliAveraging
from inquanto.protocols import BackendResultBootstrap
from inquanto.states import QubitState
from inquanto.core import BackendResult

bg_result = BackendResult

h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator

backend = AerBackend()

qubit_hamiltonian = hamiltonian.qubit_encode()

ansatz = TrotterAnsatz(
    QubitOperatorList.from_list([QubitOperator("Y0 X1 X2 X3", 1j)]),
    QubitState([1, 1, 0, 0]),
)

# One can define a computable expression, such as ExpectationValue
energy = ExpectationValue(ansatz, qubit_hamiltonian)

# We will use the PauliAveraging that needs to be built before experiments,
# that is a list of measurement circuits needs to be generated for the energy expression.
# Since there are multiple strategies to obtaine the expectation value via a quantum hardware
# we can use different protocols that specifies the way the
# measurement circuits to be generated and the distributions to be interpreted
oa = PauliAveraging(backend, shots_per_circuit=10000).build_from(
    ansatz.state_symbols.construct_from_array([-0.111]), energy
)

# We compile and run the circuits in the protocol instance
oa.compile_circuits()
oa.run(seed=0)

# The final value of the expression is computed as
result = energy.evaluate(oa.get_evaluator())

# exact: -1.137306
print(result)

# In order to resample the measurements we define a resampler:
resampler = BackendResultBootstrap(20, seed=0)

# And by using the resampler we call the oa.get_evaluators method that will return a list of evaluators
# for each sample sets.
evaluators = oa.get_evaluators_for_results(resampler)

# Note: the evaluators is just a list of evaluator functions for different samples,
# so we could do the following for example:
print(energy.evaluate(evaluators[0]))
print(energy.evaluate(evaluators[1]))

# Using the list of evaluators we can calculate the averages and standard deviations and other quantities:
print("mean:", energy.evaluate_mean(evaluators))
print("std:", energy.evaluate_std(evaluators))
print("median:", energy.evaluate_median(evaluators))
print("var:", energy.evaluate_var(evaluators))
