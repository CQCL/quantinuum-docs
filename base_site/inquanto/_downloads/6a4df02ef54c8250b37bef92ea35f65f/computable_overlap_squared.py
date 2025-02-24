r"""Computable expression example (OverlapSquared)"""
# A general way to convert familiar quantum chemistry expressions to measurement circuits.

# imports
from pytket import OpType
from pytket.extensions.qiskit import AerBackend, AerStateBackend

from inquanto.ansatzes import TrotterAnsatz
from inquanto.computables import OverlapSquared
from inquanto.operators import QubitOperatorString, QubitOperator, QubitOperatorList
from inquanto.protocols import ComputeUncompute
from inquanto.protocols import DestructiveSwapTest
from inquanto.protocols import SwapTest
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.states import QubitState

# create a first simple ansatz state
ansatz = TrotterAnsatz(
    QubitOperatorList.from_list([QubitOperator("Y0 X1 X2 X3", 1j)]),
    QubitState([1, 1, 0, 0]),
)

# copy that state and change the symbol names so we have two similar states to test overlapping
ansatz1 = ansatz.copy()
ansatz1.symbol_substitution(r"{}_1")

# instantiate backends
backend = AerBackend()
state_backend = AerStateBackend()


# make two sets of Dicts to substitute into our two states
# if the single symbol is set to the same value the states are identical and overlap^2=1
p = ansatz.state_symbols.construct_from_array([0.005])
p1 = ansatz1.state_symbols.construct_from_array([-0.111])

# combine the two dicts into 1 new one
parameters = p.copy()
parameters.update(p1)

operator = QubitOperatorString.from_string("Z0")

# protocol for |<A|B>|^2
overlap_squared1 = OverlapSquared(ansatz, ansatz1)

# protocol for  |<A|Z0|B>|^2
overlap_squared2 = OverlapSquared(ansatz, ansatz1, kernel=operator)

# first demonstrate exact evaluation with the statevector backend
sv_protocol = SparseStatevectorProtocol(state_backend)
print(f"protocol: {sv_protocol.__class__.__name__}:")
runner1 = sv_protocol.get_runner(overlap_squared1)
runner2 = sv_protocol.get_runner(overlap_squared2)
print("|<A|B>|^2 :", runner1(parameters))
print("|<A|Z0|B>|^2 :", runner2(parameters))


# make a list of protocols which can report overlap squared to iterate over for comparison
protocols = [
    ComputeUncompute(backend, 10000),
    SwapTest(backend, 10000),
    DestructiveSwapTest(backend, 10000),
]

# evaluate the computables using the various protocols and print results
for protocol in protocols:

    runner1 = protocol.get_runner(overlap_squared1)
    print(f"protocol: {protocol.__class__.__name__}:")
    print("|<A|B>|^2 :", runner1(parameters))  # runs the runner (build+run+evaluate)
    print("CX count: " + str(protocol.get_circuits()[0].n_gates_of_type(OpType.CX)))
    # print('Number of measurement circuits: ' +str(len(protocol.get_circuits())))

    runner2 = protocol.get_runner(overlap_squared2)
    print("|<A|Z0|B>|^2 :", runner2(parameters))  # runs the runner (build+run+evaluate)
    print("CX count: " + str(protocol.get_circuits()[0].n_gates_of_type(OpType.CX)))
