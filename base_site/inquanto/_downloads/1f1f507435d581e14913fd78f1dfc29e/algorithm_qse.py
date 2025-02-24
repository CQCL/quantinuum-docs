r"""A simulation of H2 in STO-3G using the QSE algorithm"""
# Import section.
import numpy as np
from pytket.extensions.qiskit import AerStateBackend

from inquanto.algorithms.qse import AlgorithmQSE
from inquanto.ansatzes import TrotterAnsatz
from inquanto.computables.composite import QSEMatricesComputable
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.operators import QubitOperator, QubitOperatorList
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.spaces import FermionSpace
from inquanto.states import QubitState

# We'll use this later to print the states
np.set_printoptions(linewidth=10000, precision=8, suppress=True)

# We will be running QSE on the H2 molecule in the STO-3G basis set. We can obtain the Hamiltonian for this system at
# equilibrium bond length via the express submodule.
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
# To encode the fermionic Hamiltonian as a qubit Hamiltonian, we can simply call the .qubit_encode() convenience method.
hamiltonian = h2.hamiltonian_operator.qubit_encode()

# We know our system has 4 spin orbitals, so we can construct a space object. We also know it is singlet spin in the
# ground state, and so we can construct a reference qubit state corresponding to the [1, 1, 0, 0] occupation number
# vector.
fermion_space = FermionSpace(4)
qubit_state = QubitState([1, 1, 0, 0])

# For this experiment, we'll construct our own ansatz by exponentiating the Y0X1X2X3 pauli-word, which corresponds to
# one double excitation.
ansatz = TrotterAnsatz(
    QubitOperatorList.from_list([QubitOperator("Y0 X1 X2 X3", 1j)]), qubit_state
)

# Now we define our operators for the expansion of the subspace. Single excitation operators are the most popular
# choice. We will constrain our single excitations to the singlet spin manifold.
expansion_operators = QubitMappingJordanWigner.operator_map(
    fermion_space.generate_subspace_singlet_singles()
)
# Now we use the inquanto.computables submodule to construct the Hamiltonian and Overlap QSE Matrices.
computable = QSEMatricesComputable(ansatz, hamiltonian, expansion_operators)

# Now we're in a position to instantiate the algorithm object and run our experiment. First, we will choose the
# parameters of our ansatz subcircuit, then pass them into the Algorithm constructor.
parameters = ansatz.state_symbols.construct_from_array([-0.10723347230091537])
algorithm = AlgorithmQSE(
    computable,
    parameters=parameters,
)

# Next we build the algorithm object, we have chosen to do a state vector simulation, and so we have also passed a
# state vector protocol instance, which tells the underlying machinery that we will evaluate our quantities of interest
# directly from the state vector.
algorithm.build(SparseStatevectorProtocol(AerStateBackend())).run()

# Show the results.
print(f"Algorithm final values: {algorithm.final_values}")
print("Algorithm final states: ")
print(algorithm.final_states)

# Compare with the exact results calculated from diagonalizing the Hamiltonian.
e = hamiltonian.eigenspectrum(qubit_state.single_term.hamming_weight)
singlet_energies = np.zeros_like(algorithm.final_values)
singlet_energies[0] = e[0]
singlet_energies[1:] = e[4:]
print(singlet_energies)
assert np.allclose(algorithm.final_values, singlet_energies)
