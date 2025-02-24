r"""An example FMO simulation of a LiH and two H2."""
import numpy as np

np.set_printoptions(linewidth=10000, precision=8, suppress=True)

from inquanto.extensions.pyscf.fmo._pyscf_fragments import (
    FMOFragmentPySCFCCSD,
    FMOFragmentPySCFRHF,
)
from inquanto.extensions.pyscf import (
    ChemistryDriverPySCFMolecularRHF,
)
from inquanto.extensions.pyscf.fmo import FMO
from inquanto.express import load_h5

from inquanto.extensions.pyscf import get_fragment_orbital_masks

driver = ChemistryDriverPySCFMolecularRHF(
    geometry=[
        ["H", [0, 0, 0]],
        ["Li", [0, 0, 1.8]],
        ["H", [0, 0, 3.0]],
        ["H", [0, 0, 3.8]],
        ["H", [0, 0, 5.0]],
        ["H", [0, 0, 5.8]],
    ],
    basis="sto3g",
    verbose=0,
)
full_integral_operator, _, _ = driver.get_system_ao(run_hf=False)

fmo = FMO(full_integral_operator)

orbitals_fr1, orbitals_fr2, orbitals_fr3 = get_fragment_orbital_masks(
    driver, [0, 1], [2, 3], [4, 5]
)

fragments = [
    FMOFragmentPySCFRHF(fmo, orbitals_fr1, 4, "Li2-1"),
    FMOFragmentPySCFRHF(fmo, orbitals_fr2, 2, "LiH-2"),
    FMOFragmentPySCFRHF(fmo, orbitals_fr3, 2, "H2-3"),
]

fmo.run(fragments)
print("# GAMESS:       -10.0106046405")
