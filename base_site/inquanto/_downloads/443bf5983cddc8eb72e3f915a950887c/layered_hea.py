r"""Use of a layered hardware efficient Ansatz."""

# imports
from pytket import OpType

from inquanto.ansatzes import HardwareEfficientAnsatz
from inquanto.spaces import FermionSpace
from inquanto.states import QubitState

# Here we create a layered hardware efficient ansatz for a 4 spin-orbital fock space with 2 electrons.
space = FermionSpace(4)
state = QubitState([1, 1, 0, 0])
ansatz = HardwareEfficientAnsatz([OpType.Rx, OpType.Ry], state, n_layers=2)

# each layer for a 4 qubit system needs 3 entangling operations
print("\n HEA CNOT GATES:  {}".format(ansatz.circuit_resources()["gates_2q"]))
