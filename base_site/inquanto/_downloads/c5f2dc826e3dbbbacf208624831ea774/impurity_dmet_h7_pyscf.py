r"""An ImpurityDMET example simulating a 7-hydrogen chain."""

# imports
from inquanto.extensions.pyscf import (  # inquanto-pyscf extension required here
    ChemistryDriverPySCFMolecularROHF,
    ImpurityDMETROHFFragmentPySCFROHF,
    get_fragment_orbital_masks,
)

from inquanto.embeddings import ImpurityDMETROHF

# prepare variable 3 x h2 ring +1
d = 2.0
g_H3_H4 = [
    ["H", [2, 0, 0]],
    ["H", [1, 0, 0]],
    ["H", [0, 0, 0]],
    ["H", [0, 0, d]],
    ["H", [0, 0, d + 1]],
    ["H", [0, 0, d + 2]],
    ["H", [0, 0, d + 3]],
]

# get the localized ham and rdms for our 3xh2+1 system
driver = ChemistryDriverPySCFMolecularROHF(
    basis="sto-3g", geometry=g_H3_H4, charge=0, multiplicity=2
)
hamiltonian_operator, space, rdm1 = driver.get_lowdin_system()

# define impurity dmet solver using full localized hamiltonian
dmet = ImpurityDMETROHF(hamiltonian_operator, rdm1, occupation_atol=1e-7)

# mask off a h3 fragment and
print("\n=== H3 ===\n")
(mask_H3,) = get_fragment_orbital_masks(driver, [0, 1, 2])

fragment = ImpurityDMETROHFFragmentPySCFROHF(dmet, mask_H3, multiplicity=2)

# solve the impurity dmet
result = dmet.run(fragment)
print("ROHF energy (ref)   :  ", driver.mf_energy)
print("Impurity DMET (ROHF):  ", result)
