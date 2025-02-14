r"""Protocol observable averaging to calculate expectation values."""

# imports
from sympy import Symbol
from pytket.extensions.qiskit import AerBackend, AerStateBackend
from pytket.partition import PauliPartitionStrat
from pytket import OpType

from inquanto.computables import ExpectationValue
from inquanto.ansatzes import TrotterAnsatz
from inquanto.express import load_h5
from inquanto.operators import QubitOperatorList
from inquanto.protocols import PauliAveraging, SparseStatevectorProtocol
from inquanto.states import QubitState


# use express to load in an example system
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
qubit_hamiltonian = h2.hamiltonian_operator.qubit_encode()

# prepare a minimal ansatz
exponents = QubitOperatorList.from_string("theta [(1j, Y0 X1 X2 X3)]")
reference = QubitState([1, 1, 0, 0])
ansatz = TrotterAnsatz(exponents, reference)

parameters = {Symbol("theta"): -0.111}
backend = AerBackend()

# define a quantum computable quantity
energy = ExpectationValue(ansatz, qubit_hamiltonian)

# instantiate a statevector protocol to use as an evaluator of the exp val
protocol_sv = SparseStatevectorProtocol(AerStateBackend())
sv_evaluator = protocol_sv.get_evaluator(parameters)
sv_energy_value = energy.evaluate(evaluator=sv_evaluator)
print("Statevector: " + str(sv_energy_value))

# set up a shot based protocol to calculate the expval
protocol = PauliAveraging(
    backend,
    shots_per_circuit=1000,
    pauli_partition_strategy=PauliPartitionStrat.CommutingSets,
)

# build and run the protocol for the computable data
protocol.build_from(parameters, energy).compile_circuits()

# inspect the built circuits
print("Number of measurement circuits: " + str(len(protocol.get_circuits())))
print("CX count: " + str(protocol.get_circuits()[0].n_gates_of_type(OpType.CX)))

protocol.run(seed=0)

# evaluate the computable using the circuits
energy_value = energy.evaluate(protocol.get_evaluator())
print("Shot based: " + str(energy_value))
