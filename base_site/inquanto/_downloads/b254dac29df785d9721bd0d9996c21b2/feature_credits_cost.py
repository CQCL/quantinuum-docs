r"""Protocol observable averaging to calculate expectation values."""

# imports
from pytket.partition import PauliPartitionStrat
from pytket.extensions.quantinuum import QuantinuumBackend

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

# instantiate the quantinuum backend
# target the H1-1 device, but the machine_debug option prevents querying the online
# quantinuum api (no credentials needed)
backend = QuantinuumBackend("H1-1", machine_debug=True)

protocol = PauliAveraging(
    backend,
    shots_per_circuit=1000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)

# use the protocol to build the measurement circuits for the backend
# this takes the computable (ansatz, kernel) tuple
protocol.build(parameters, ansatz, qubit_hamiltonian)

# when you have the measurement circuits the full cost of the protocol can be evaluated


# these commented functions require the user  to resolve the Quantinuum log-in prompt
# print(protocol.cost())
# print(protocol.credits("H1-1SC", False))

# dataframe can be inspected
