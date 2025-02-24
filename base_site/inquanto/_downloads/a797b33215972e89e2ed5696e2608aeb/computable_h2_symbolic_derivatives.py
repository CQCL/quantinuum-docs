r"""Use of computables classes for STO-3G H2 expectation value and gradients with symbolic protocol."""

# imports
from pytket.extensions.qiskit import AerStateBackend

from inquanto.ansatzes import TrotterAnsatz
from inquanto.computables import (
    ExpectationValue,
    ExpectationValueDerivative,
    ComputableTuple,
)

# H2 STO-3G Hamiltonian
from inquanto.express import load_h5
from inquanto.operators import QubitOperator, QubitOperatorList
from inquanto.protocols import (
    SymbolicProtocol,
    SparseStatevectorProtocol,
)
from inquanto.states import QubitState

# load in H2 sto_3g system
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator

backend = AerStateBackend()

qubit_hamiltonian = hamiltonian.qubit_encode()

# prepare a minimal ansatz state with a single specific qubit operator
ansatz = TrotterAnsatz(
    QubitOperatorList.from_list([QubitOperator("Y0 X1 X2 X3", 1j)]),
    QubitState([1, 1, 0, 0]),
)

# One can define a computable expression, such as ExpectationValue
energy = ExpectationValue(ansatz, qubit_hamiltonian)
energy_gradient = ExpectationValueDerivative(
    ansatz, qubit_hamiltonian, ansatz.free_symbols_ordered()
)

# use a ComputableTuple to hold both the energy and gradient computables
c = ComputableTuple(energy, energy_gradient)

parameters = ansatz.state_symbols.construct_from_array([-0.111])


# This SymbolicProtocol uses Sympy to perform symbolic evaluation and is limited to small systems
# this runner will evaluate both computables in the ComputableTuple
sym_runner = SymbolicProtocol().get_runner(c)
# evaluate the symbolic runner by providing the ansatz parameters to obtain results
print(sym_runner(parameters))

sv_runner = SparseStatevectorProtocol(backend).get_runner(c)
# evaluate the statevector runner by providing the ansatz parameters to obtain results
print(sv_runner(parameters))
