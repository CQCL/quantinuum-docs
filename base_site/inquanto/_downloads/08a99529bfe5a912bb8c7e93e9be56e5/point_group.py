r"""Use of PointGroup class containing point group symmetry information."""

# imports
from inquanto.symmetry import PointGroup

# one can instantiate a point group object which is useful throughout InQuanto, especially in FermionSpace and similar
# objects, for reducing problem sizes. In general a user will not need to interface with these objects, but examples
# of how they can be used are included in any case

# take reduced point group for H2 Dooh -> D2h
pg = PointGroup("D2h")

# the character table can be pretty-printed using the native function
pg.print_character_table()

# spin orbital symmetries in minimal basis H2
orbital_irreps = ["Ag", "Ag", "B1u", "B1u"]

# one can calculate the direct product of the irreps of orbitals like so
irrep_coefficients, character_direct_product = pg.irrep_direct_product(["Ag", "B1u"])

print("Ag x B1u direct product irrep coefficients:", irrep_coefficients)
print("Ag x B1u character direct product:         ", character_direct_product)

# a list of supported point groups can be obtained with
pg.supported_groups()
