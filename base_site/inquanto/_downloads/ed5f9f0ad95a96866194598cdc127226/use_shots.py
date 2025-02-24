r"""Example of the usage of the CuTensorNetShotsBackend backend with inquanto."""

from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.computables import Overlap
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.operators import QubitOperator
from inquanto.protocols import HadamardTestOverlap
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState
from pytket.extensions.cutensornet import CuTensorNetShotsBackend
from pytket.extensions.qiskit import AerBackend

h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator
qubit_hamiltonian = hamiltonian.qubit_encode()
space = FermionSpace(4)
state = FermionState([1, 1, 0, 0])
ansatz = FermionSpaceAnsatzUCCSD(space, state, QubitMappingJordanWigner())
parameters = ansatz.state_symbols.construct_random()

overlap = Overlap(ansatz, ansatz)

# Use the qiskit backend
protocol = HadamardTestOverlap(backend=AerBackend(), shots_per_circuit=10000)
executor = protocol.get_runner(overlap, compile_symbolic=True)
print(executor(parameters))

# Use the cuTensorNet backend
protocol = HadamardTestOverlap(
    backend=CuTensorNetShotsBackend(), shots_per_circuit=10000
)
executor = protocol.get_runner(overlap, compile_symbolic=True)
print(executor(parameters))
