r"""An example FMO simulation of a 3-dihydrogen chain with CCSD fragment solver."""
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

driver = ChemistryDriverPySCFMolecularRHF(
    geometry=[
        ["H", [0, 0, 0]],
        ["H", [0, 0, 0.8]],
        ["H", [0, 0, 2.0]],
        ["H", [0, 0, 2.8]],
        ["H", [0, 0, 4.0]],
        ["H", [0, 0, 4.8]],
    ],
    basis="sto3g",
    verbose=0,
)
full_integral_operator, _, _ = driver.get_system_ao(run_hf=False)

fmo = FMO(full_integral_operator)

fragments = [
    FMOFragmentPySCFCCSD(fmo, [True, True, False, False, False, False], 2, "H2-1"),
    FMOFragmentPySCFCCSD(fmo, [False, False, True, True, False, False], 2, "H2-2"),
    FMOFragmentPySCFCCSD(fmo, [False, False, False, False, True, True], 2, "H2-3"),
]

fmo.run(fragments)
print("# GAMESS:       -3.3512756041999996")
