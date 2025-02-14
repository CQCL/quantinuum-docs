r"""Finding fermionic Z2 symmetry operators."""

# imports
from inquanto.express import load_h5
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState

# Load the Hamiltonian, define HF state and symmetry information
h2 = load_h5("h2_sto3g_symmetry.h5", as_tuple=True)
hamiltonian_operator = h2.hamiltonian_operator.to_FermionOperator()
state = FermionState([1, 1, 0, 0])

point_group_label = "D2h"
orbital_irrep_labels = ["Ag", "Ag", "B1u", "B1u"]
space = FermionSpace(4, point_group=point_group_label, orb_irreps=orbital_irrep_labels)
space_from_express = h2.fermion_space
print(
    "Do manual and express orb irreps match? ",
    space.orb_irreps() == space_from_express.orb_irreps(),
)

# Generate the symmetry operators - observing the output, we see the first symmetry operator is the point group symmetry, the second is the number
# parity operator, and the third is the spin parity operator.
symmetry_operators = space.symmetry_operators_z2()
print("#### SYMMETRY OPERATORS ####")
for sym_op in symmetry_operators:
    print(sym_op)

######## OUTPUT ########
#### SYMMETRY OPERATORS ####
# (1) [] + (-2) [F3^ F3 ] + (-2) [F2^ F2 ] + (4) [F2^ F2  F3^ F3 ]
# (1) [] + (-2) [F3^ F3 ] + (-2) [F2^ F2 ] + (4) [F2^ F2  F3^ F3 ] + (-2) [F1^ F1 ] + (4) [F1^ F1  F3^ F3 ] + (4) [F1^ F1  F2^ F2 ] + (-8) [F1^ F1  F2^ F2  F3^ F3 ] + (-2) [F0^ F0 ] + (4) [F0^ F0  F3^ F3 ] + (4) [F0^ F0  F2^ F2 ] + (-8) [F0^ F0  F2^ F2  F3^ F3 ] + (4) [F0^ F0  F1^ F1 ] + (-8) [F0^ F0  F1^ F1  F3^ F3 ] + (-8) [F0^ F0  F1^ F1  F2^ F2 ] + (16) [F0^ F0  F1^ F1  F2^ F2  F3^ F3 ]
# (1) [] + (-2) [F2^ F2 ] + (-2) [F0^ F0 ] + (4) [F0^ F0  F2^ F2 ]
#########################

# We can validate that the obtained symmetries are indeed symmetries of the fermionic Hamiltonian
is_valid_symmetry_test = [
    x.is_symmetry_of(hamiltonian_operator) for x in symmetry_operators
]
print("Valid symmetries: {}".format(is_valid_symmetry_test))

# OUTPUT: Valid symmetries: [True, True, True]

# We can also calculate which symmetry sector a given fermionic state is in:
symmetry_sector = [x.symmetry_sector(state) for x in symmetry_operators]
print("Symmetry sector: {}".format(symmetry_sector))

# OUTPUT: Symmetry sector: [1, 1, -1]
