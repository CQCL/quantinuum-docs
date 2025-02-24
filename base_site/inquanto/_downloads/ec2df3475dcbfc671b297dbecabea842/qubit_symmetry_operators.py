r"""Finding qubit Z2 symmetry operators."""

# imports
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.spaces import FermionSpace, QubitSpace
from inquanto.states import FermionState

# Load the fermionic Hamiltonian, define HF state and map to qubits
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian_operator = h2.hamiltonian_operator.to_FermionOperator()
fermion_space = FermionSpace(4)
hf_state = FermionState([1, 1, 0, 0])
qubit_space = QubitSpace(4)
qubit_hamiltonian = QubitMappingJordanWigner.operator_map(hamiltonian_operator)
qubit_hf_state = QubitMappingJordanWigner.state_map(hf_state)

# Generate the symmetry operators from the Hamiltonian - we find three.
symmetry_operators = qubit_space.symmetry_operators_z2(qubit_hamiltonian)
print("#### SYMMETRY OPERATORS ####")
for sym_op in symmetry_operators:
    print(sym_op)

######## OUTPUT ########
#### SYMMETRY OPERATORS ####
# (1.00000000000000) [Z0 I1 Z2 I3]
# (1.00000000000000) [I0 Z1 Z2 I3]
# (1.00000000000000) [I0 I1 Z2 Z3]
#########################

# We can validate that the obtained symmetries are indeed symmetries of the fermionic Hamiltonian
is_valid_symmetry_test = [
    x.is_symmetry_of(qubit_hamiltonian) for x in symmetry_operators
]
print("Valid symmetries: {}".format(is_valid_symmetry_test))

# OUTPUT: Valid symmetries: [True, True, True]

# We can also calculate which symmetry sector a given fermionic state is in:
symmetry_sector = [x.symmetry_sector(qubit_hf_state) for x in symmetry_operators]
print("Symmetry sector: {}".format(symmetry_sector))

# OUTPUT: Symmetry sector: [1, 1, -1]
