r"""An Impurity DMET example for simulating a 3-dihydrogen ring."""
from typing import List, Tuple

import numpy as np
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

from inquanto.embeddings import DMETRHF, DMETRHFFragment, ImpurityDMETROHF
from inquanto.express import list_h5, load_h5
from inquanto.operators import ChemistryRestrictedIntegralOperator

h2_3_ring_sto3g = load_h5("h2_3_ring_sto3g.h5", as_tuple=True)

print("HF energy (ref):  ", h2_3_ring_sto3g.energy_hf)
print(
    "HF energy (trace):",
    h2_3_ring_sto3g.hamiltonian_operator_lowdin.energy(
        h2_3_ring_sto3g.one_body_rdm_hf_lowdin
    ),
)

# define dmet solver
dmet = ImpurityDMETROHF(
    h2_3_ring_sto3g.hamiltonian_operator_lowdin, h2_3_ring_sto3g.one_body_rdm_hf_lowdin
)

fragment = ImpurityDMETROHFFragmentPySCFCCSD(
    dmet, np.array([True, True, False, False, False, False]), frozen=[0, 3]
)

result = dmet.run(fragment)
print(result)

# -3.2341571951577137 2.7040838812553147e-06
# -3.2341571951577137
