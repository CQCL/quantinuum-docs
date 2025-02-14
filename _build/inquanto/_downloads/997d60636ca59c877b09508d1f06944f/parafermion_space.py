r"""Use of ParaFermionSpace objects to generate parafermionic states and operators."""

# imports
from inquanto.spaces import ParaFermionSpace
from inquanto.symmetry import PointGroup

# create a FermionSpace object
space = ParaFermionSpace(8)

# with the state and space objects we can construct operators using native functions, for example:
singles = space.construct_single_qubit_excitation_operators()
doubles = space.construct_double_qubit_excitation_operators()
qubit_excitations = singles + doubles

print("number of qubit excitations for minimal basis h2:", len(qubit_excitations))

# we can point group filter in this way as in the regular fermionic case
space = ParaFermionSpace(
    8,
    point_group=PointGroup("D2h"),
    orb_irreps=["Ag", "Ag", "B1u", "B1u", "B2u", "B2u", "Ag", "Ag"],
)
singles = space.construct_single_qubit_excitation_operators()
doubles = space.construct_double_qubit_excitation_operators()
qubit_excitations = singles + doubles

print(
    "number of symmetry permitted qubit excitations for minimal basis h2:",
    len(qubit_excitations),
)
