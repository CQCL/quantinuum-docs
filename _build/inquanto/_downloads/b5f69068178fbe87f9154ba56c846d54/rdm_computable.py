r"""An example for constructing an RDM using computables"""
import numpy

from inquanto.ansatzes import TrotterAnsatz
from inquanto.computables.composite import (
    RestrictedOneBodyRDMComputable,
    RestrictedOneBodyRDMRealComputable,
)
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.operators import QubitOperator, QubitOperatorList
from inquanto.protocols import (
    PauliAveraging,
)
from inquanto.spaces import FermionSpace
from inquanto.states import QubitState
from pytket.partition import PauliPartitionStrat

numpy.set_printoptions(linewidth=10000, precision=8, suppress=True)

# pip install pytket-qiskit==0.18
from pytket.extensions.qiskit import AerBackend, AerStateBackend

# from from qiskit_aer.noise import ReadoutError, NoiseModel
# from pytket.extensions.qulacs import QulacsBackend

h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator.qubit_encode()

space = FermionSpace(4)

ansatz = TrotterAnsatz(
    QubitOperatorList.from_list([QubitOperator("Y0 X1 X2 X3", 1j)]),
    QubitState([1, 1, 0, 0]),
)
parameters = ansatz.state_symbols.construct_from_array([0])
m = RestrictedOneBodyRDMRealComputable(space, ansatz, QubitMappingJordanWigner())

print("PauliAveraging NonConflictingSets")
evaluator = (
    PauliAveraging(
        AerBackend(),
        10000,
        pauli_partition_strategy=PauliPartitionStrat.NonConflictingSets,
    )
    .build_from(parameters, m)
    .compile_circuits()
    .run(seed=0)
    .get_evaluator()
)
rdm1 = m.evaluate(evaluator)

print(h2.energy_hf)
energy = h2.hamiltonian_operator.energy(rdm1)
print(energy)

assert abs(h2.energy_hf - energy) < 1e-4

print("PauliAveraging CommutingSets")
evaluator = (
    PauliAveraging(
        AerBackend(), 10000, pauli_partition_strategy=PauliPartitionStrat.CommutingSets
    )
    .build_from(parameters, m)
    .compile_circuits()
    .run(seed=0)
    .get_evaluator()
)
rdm1 = m.evaluate(evaluator)


print(h2.energy_hf)
energy = h2.hamiltonian_operator.energy(rdm1)
print(energy)

assert abs(h2.energy_hf - energy) < 1e-4

print("SparseStatevectorProtocol")
rdm1 = m.default_evaluate(ansatz.state_symbols.construct_from_array([0]))

print(h2.energy_hf)
energy = h2.hamiltonian_operator.energy(rdm1)
print(energy)

assert abs(h2.energy_hf - energy) < 1e-12
