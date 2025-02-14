r"""Partition measurement reduction strategies for PauliAveraging protocol."""

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

# get a shot based backend from pytket extensions
backend = AerBackend()
print("Qubit hamiltonian has ", len(qubit_hamiltonian), " terms")
# The constant term doesn't require measurement
print(qubit_hamiltonian.df())

# build circuits without partitioning
protocol = PauliAveraging(
    backend,
    shots_per_circuit=1000,
    pauli_partition_strategy=None,
)
protocol.build(parameters, ansatz, qubit_hamiltonian)
print("No partitioning:", protocol.n_circuit, " measurement circuits")
# print(protocol.dataframe_partitioning())

# build circuits with CommutingSet partitioning of Pauli operators
# see pytket.partition documentation for more details
protocol = PauliAveraging(
    backend,
    shots_per_circuit=1000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)
protocol.build(parameters, ansatz, qubit_hamiltonian)
print("Commuting sets:", protocol.n_circuit, " measurement circuits")
# print(protocol.dataframe_partitioning())


# build circuits with NonConflicting partitioning of Pauli operators
protocol = PauliAveraging(
    backend,
    shots_per_circuit=1000,
    pauli_partition_strategy=PauliPartitionStrat.NonConflictingSets,
)
protocol.build(parameters, ansatz, qubit_hamiltonian)
print("Non Conflicting sets:", protocol.n_circuit, " measurement circuits")
print(protocol.dataframe_partitioning())
