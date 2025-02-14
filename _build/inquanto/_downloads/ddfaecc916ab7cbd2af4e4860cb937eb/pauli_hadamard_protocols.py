r"""Usage of the PauliAveraging and HadamardTest protocols."""

# imports
from pytket.extensions.qiskit import AerBackend
from pytket.partition import PauliPartitionStrat

from inquanto.express import load_h5
from inquanto.ansatzes import TrotterAnsatz
from inquanto.operators import QubitOperatorList
from inquanto.states import QubitState
from inquanto.protocols import PauliAveraging, HadamardTest

# load example system from express database
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
qubit_hamiltonian = h2.hamiltonian_operator.qubit_encode()

# create a simple state
exponents = QubitOperatorList.from_string("theta [(1j, Y0 X1 X2 X3)]")
reference = QubitState([1, 1, 0, 0])
ansatz = TrotterAnsatz(exponents, reference)
parameters = dict(theta=-0.111)

## Using PauliAveraging
protocol_pa = PauliAveraging(
    AerBackend(),
    shots_per_circuit=1000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)

protocol_pa.build(parameters, ansatz, qubit_hamiltonian).compile_circuits()
print("PA number circuits", len(protocol_pa.get_circuits()))
protocol_pa.run(seed=0)
energy_value = protocol_pa.evaluate_expectation_value(ansatz, qubit_hamiltonian)
print(energy_value)

## Using HadamardTest
protocol_ht = HadamardTest(
    AerBackend(),
    shots_per_circuit=1000,
)

protocol_ht.build(parameters, ansatz, qubit_hamiltonian).compile_circuits()
print("HT number circuits", len(protocol_ht.get_circuits()))
protocol_ht.run(seed=0)
energy_value = protocol_ht.evaluate_expectation_value(ansatz, qubit_hamiltonian)
print(energy_value)
