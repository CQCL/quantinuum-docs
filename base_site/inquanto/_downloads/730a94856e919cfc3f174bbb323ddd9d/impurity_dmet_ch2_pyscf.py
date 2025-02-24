r"""An example for running impurity DMET on triplet CH2."""

# imports
from typing import List, Tuple

import numpy as np

# used and example impurity embedding classes
from inquanto.extensions.pyscf import (  # inquanto-pyscf extension required here
    ChemistryDriverPySCFMolecularRHF,
    ChemistryDriverPySCFMolecularROHF,
    ImpurityDMETROHFFragmentPySCFActive,
    ImpurityDMETROHFFragmentPySCFCCSD,
    ImpurityDMETROHFFragmentPySCFFCI,
    ImpurityDMETROHFFragmentPySCFMP2,
    ImpurityDMETROHFFragmentPySCFROHF,
    get_fragment_orbital_masks,
)

from inquanto.embeddings import DMETRHFFragment, ImpurityDMETROHF
from inquanto.operators import ChemistryRestrictedIntegralOperator

# methyl geometry
g_CH2 = """
C1	0.000	0.000	0.124
H2	0.000	0.962	-0.371
H3	0.000	-0.962	-0.371
"""

# obtain full triplet methyl fermionic system in localized lowdin orbitals
driver = ChemistryDriverPySCFMolecularROHF(
    basis="3-21G", geometry=g_CH2, charge=0, multiplicity=3
)

hamiltonian_operator, space, rdm1 = driver.get_lowdin_system()

# define impurity dmet solver using the full localized system
dmet = ImpurityDMETROHF(hamiltonian_operator, rdm1, occupation_atol=1e-5)

# perform impurity dmet using RHF meanfield C fragment
print("\n=== C RHF ===\n")
(mask_C,) = get_fragment_orbital_masks(driver, [0])

# inquanto-pyscf class for embedded ROHF
fragment = ImpurityDMETROHFFragmentPySCFROHF(dmet, mask_C, multiplicity=3)

result = dmet.run(fragment)
print("ROHF energy (ref)   :  ", driver.mf_energy)
print("Impurity DMET (ROHF):  ", result)


# perform impurity dmet using FCI C fragment
print("\n=== C FCI ===\n")
(mask_C,) = get_fragment_orbital_masks(driver, [0])

# inquanto-pyscf class for embedded FCI
fragment = ImpurityDMETROHFFragmentPySCFFCI(dmet, mask_C)

result = dmet.run(fragment)
print("ROHF energy (ref)   :  ", driver.mf_energy)
print("Impurity DMET (FCI) :  ", result)


# Impurity DMET (FCI) :   -38.772955250239576  mult=1
# Impurity DMET (FCI) :   -38.772955250397146  mult=3
