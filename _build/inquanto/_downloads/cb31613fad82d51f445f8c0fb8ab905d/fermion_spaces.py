r"""Use of FermionSpace objects to generate fermionic states and operators, including point group symmetry."""

# imports
import numpy as np

from inquanto.spaces import FermionSpace
from inquanto.states import FermionState
from inquanto.symmetry import PointGroup

# create a FermionSpace object for, say, H2
space = FermionSpace(4)
state = FermionState([1, 1, 0, 0])

# with the state and space objects we can construct operators using native functions, for example:
singles = space.construct_single_ucc_operators(state)
doubles = space.construct_double_ucc_operators(state)
uccsd_excitations = singles + doubles
print("number of uccsd excitations for minimal basis h2:", len(uccsd_excitations))

# we can also pass symmetry information to remove redundant excitations
space = FermionSpace(
    4, point_group=PointGroup("D2h"), orb_irreps=["Ag", "Ag", "B1u", "B1u"]
)
singles = space.construct_single_ucc_operators(state)
doubles = space.construct_double_ucc_operators(state)
# there are many other constructor methods (e.g. generalized)
uccsd_excitations = singles + doubles

print(
    "number of allowed uccsd excitations for minimal basis h2:", len(uccsd_excitations)
)

# any state defined in the FermionSpace can be pretty-printed by the space object
print("fock state:")
space.print_state(state)

# we can use the state object to create an occupation state with a given multiplicity
triplet_state = space.generate_occupation_state(n_fermion=2, multiplicity=3)
print("triplet state:")
space.print_state(triplet_state)

# likewise, spatial occupations can be used to generate a state and from spin occupation lists
space.generate_occupation_state_from_spatial_occupation([2, 0])
space.generate_occupation_state_from_list([1, 1, 0, 0])

# many operators are accessible through the space object, for example
space.construct_orbital_number_operators()
space.construct_number_operator()
space.construct_sz_operator()
space.construct_spin_operator()

# similar behavior for periodic systems can be seen in FermionSpaceBrillouin and FermionSpaceSupercell
