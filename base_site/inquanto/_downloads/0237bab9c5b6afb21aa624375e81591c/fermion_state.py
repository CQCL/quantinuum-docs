r"""Creation of FermionState objects and demonstration of some functionality."""

# imports
import numpy

from sympy import Symbol

from inquanto.states import FermionState, FermionStateString

# create a h2 fock state
h2_fock = FermionState([1, 1, 0, 0])
print("Is this a basis state? ", h2_fock.is_basis_state())
print("How many fermionic modes in state:", h2_fock.num_modes)


# doubly excited state
h2_double = FermionState([0, 0, 1, 1])

# compute dot product
print("hf X double exc, dot product:", h2_fock.vdot(h2_double))
# states are orthogonal

# dot product with single excited state
print("hf X single exc, dot product:", h2_fock.vdot(FermionState([0, 1, 1, 0])))
# states are orthogonal

#
print("fock dot fock", h2_fock.vdot(h2_fock))

# return the state as a list, helpful when the FermionState is returned from a driver or other routine
print("fock state as list:", h2_fock.single_term.occupations_ordered())
print("")

# linear combinations of states
# normalized
coeff1, coeff2 = numpy.sqrt(0.75), numpy.sqrt(0.25)
fss1 = FermionStateString([1, 1, 0, 0])
fss2 = FermionStateString([0, 0, 1, 1])
fs_dict = FermionState({fss1: coeff1, fss2: coeff2})
fs_tuple = FermionState(((coeff1, fss1), (coeff2, fss2)))
print(fs_dict)

print("Is this a basis state? ", fs_dict.is_basis_state())
# false as linear combination of basis states
print("Is this state normalized? ", fs_dict.is_normalized())
# true as sum = 1
print("")

# unnormalized linear combination example with complex coeff
coeff1, coeff2 = numpy.sqrt(1.25 + 0.1j), numpy.sqrt(0.25)
fs_dict = FermionState({fss1: coeff1, fss2: coeff2})
fs_tuple = FermionState(((coeff1, fss1), (coeff2, fss2)))
print(fs_dict)
print("Is this state normalized? ", fs_dict.is_normalized())
print("Is this coefficient complex? ", fs_dict.is_any_coeff_complex())

fs_dict.print_table()
print("")

# coefficients of fermion states can be symbolic
sym_coeff = Symbol("a_1")
sym_coeff2 = Symbol("b_1")
fs_dict = FermionState({fss1: sym_coeff2, fss2: sym_coeff})
print("Free symbols before substitution", fs_dict.free_symbols())
# note: can't normalize symbolic states
simple_sd = {sym_coeff: 1.1, sym_coeff2: 0.1}

# insert numeric values into symbolic state
fs_dict.symbol_substitution(simple_sd)
print("Free symbols after substitution", fs_dict.free_symbols())
# we can renormalize our numeric state coefficients
fs_dict = fs_dict.normalized()
fs_dict.print_table()
# some further related examples can found in ansatze/multiconfig
