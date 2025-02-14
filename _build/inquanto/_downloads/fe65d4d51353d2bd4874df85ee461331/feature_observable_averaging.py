r"""Protocol observable averaging to calculate expectation values."""

# imports
from pytket.partition import PauliPartitionStrat
from pytket.extensions.qiskit import AerBackend

from inquanto.ansatzes import TrotterAnsatz
from inquanto.express import load_h5
from inquanto.operators import QubitOperatorList
from inquanto.protocols import PauliAveraging
from inquanto.states import QubitState

# get an example system from express database
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
qubit_hamiltonian = h2.hamiltonian_operator.qubit_encode()

# make a very small ansatz state
exponents = QubitOperatorList.from_string("theta [(1j, Y0 X1 X2 X3)]")
reference = QubitState([1, 1, 0, 0])
ansatz = TrotterAnsatz(exponents, reference)
parameters = dict(theta=-0.111)

backend = AerBackend()

protocol = PauliAveraging(
    backend,
    shots_per_circuit=1000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)

# PauliAveraging can evaluate expectation values, in this case of
# the qubit hamiltonian on the ansatz state. The build() method constructs and compiles measurement circuits
protocol.build(parameters, ansatz, qubit_hamiltonian).compile_circuits()

# circuit and measurement dataframes can be inspected
print(protocol.dataframe_measurements())
print(protocol.dataframe_circuit_shot())

# we can pickle protocols to reload later
pickled_data = protocol.dumps()

# internal data of protocols can be cleared for reuse
print(protocol.is_built, protocol.is_run)
protocol.clear()
print(protocol.is_built, protocol.is_run)

# load back pickled data
new_protocol = PauliAveraging.loads(pickled_data, backend)

# we can run the protocols
new_protocol.run(seed=0)
print(new_protocol.dataframe_measurements())

# we can also launch/retrieve
handles = new_protocol.launch(seed=1)
new_protocol.retrieve(handles)
print(new_protocol.dataframe_measurements())

# We can use results to evaluate any expectation value with a kernel consisting of the same pauli words
energy_value = new_protocol.evaluate_expectation_value(ansatz, qubit_hamiltonian)
print(energy_value)

# can evaluate any qubit_hamiltonian that has the same pauli strings
energy_value = new_protocol.evaluate_expectation_value(ansatz, 2.3 * qubit_hamiltonian)
print(energy_value)

# can evaluate any qubit_hamiltonian that has the same pauli strings with stderr
energy_uvalue = new_protocol.evaluate_expectation_uvalue(
    ansatz, 2.3 * qubit_hamiltonian
)
print(energy_uvalue)
