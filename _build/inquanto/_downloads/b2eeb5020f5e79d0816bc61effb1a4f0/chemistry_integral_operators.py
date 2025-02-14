r"""Creation of ChemistryRestrictedIntegralOperator (CRIO) and conversion to FermionOperator."""

# imports
import numpy as np

from inquanto.express import load_h5
from inquanto.operators import ChemistryRestrictedIntegralOperator, RestrictedOneBodyRDM

# obtain a model system from express
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
ham = h2.hamiltonian_operator  # this is a ChemistryIntegral object
print(type(ham))

# we can manually define an RDM
rdm1 = np.array([[2, 0], [0, 0]])
rdm1 = RestrictedOneBodyRDM(rdm1)
# and compute the total mean-field energy with the set rdm and the integral operator
print("energy =", ham.energy(rdm1))
# other observables can also be computed
print("effective Coulomb potential = ")
print(ham.effective_potential(rdm1))

# map hamiltonian in ChemistryRestrictedIntegralOperator to qubit representation
# this method defaults to Jordan-Wigner mapping
qubit_hamiltonian = ham.qubit_encode()

# create FermionOperator object from the crio
ham = ham.to_FermionOperator()
print("Hamiltonian dataframe:")
print(ham.df())
# see FermionOperator examples for functional examples after conversion

# The fermion to CRIO method assumes spin-restricted
crio_from_fo = ChemistryRestrictedIntegralOperator.from_FermionOperator(ham)

# A chemistry integral object can be rewritten in a memory efficient form
# by storing a two-body integral tensor in s4/s8 symmetry reduced form.
crio_compact = crio_from_fo.to_compact_integral_operator(symmetry="s8")
print(crio_compact.df())

"""
# One can also create CRIO from an fcidump file generated 
# by various chemistry codes e.g.
from inquanto.operators import FCIDumpRestricted
fdr = FCIDumpRestricted()
fdr.load('file.fcidump')
fham = fdr.to_ChemistryRestrictedIntegralOperator()
"""
