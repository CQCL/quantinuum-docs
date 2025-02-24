r"""Use of computables classes for STO-3G H2 expectation value measurement."""
# Computable expression example (ExpectationValue):
# A general way to convert familiar quantum chemistry expressions to measurement circuits.

# imports
from pytket.extensions.qiskit import AerBackend

from inquanto.ansatzes import TrotterAnsatz
from inquanto.computables import ExpectationValue

from inquanto.express import load_h5
from inquanto.operators import QubitOperator, QubitOperatorList
from inquanto.protocols import PauliAveraging
from inquanto.states import QubitState

# H2 STO-3G Hamiltonian from express
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

# there are multiple strategies to evaluate the expectation value and we
# use different protocols to represent these various strategies.

# The PauliAveraging protocol needs to be built before running experiments.
# Building yields a list of measurement circuits for the energy expression.
# It also contains instruction for the interpretation of distributions

oa = PauliAveraging(backend, 10000)

# build_from builds the circuits need for evaluating the computable
# and also requires a set of symbol values to substituted in
oa.build_from(ansatz.state_symbols.construct_from_array([-0.111]), energy)
print("Did the protocol build? " + str(oa.is_built))

oa.compile_circuits()

# We launch and retrieve the circuits in the protocol instance
# This can alternatively be done synchronously by calling oa.run(seed = 0)
handles = oa.launch(seed=0)
oa.retrieve(handles)

# The final value of the expression is computed as:
result = energy.evaluate(oa.get_evaluator())
# note that this evaluation does not make or run any circuits, it uses the results
# contained in the protocol to evaluate the computable


# exact: -1.137306
print(result)

# One can repeat the measurements multiple times to see how the results vary
for i in range(3):
    oa.run(seed=i)
    result = energy.evaluate(oa.get_evaluator())
    print(f"{i}:", result)

# to show statistics about the measured pauli strings
print(oa.dataframe_measurements())
# to examine which pauli strings are measured by which circuit
print(oa.dataframe_partitioning())
# to examine properties of the measurement circuits
print(oa.dataframe_circuit_shot())
