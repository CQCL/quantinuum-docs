r"""An example FMO simulation of a 3-dihydrogen chain."""
import numpy

numpy.set_printoptions(linewidth=10000, precision=8, suppress=True)

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
    FMOFragmentPySCFRHF(fmo, [True, True, False, False, False, False], 2, "H2-1"),
    FMOFragmentPySCFRHF(fmo, [False, False, True, True, False, False], 2, "H2-2"),
    FMOFragmentPySCFRHF(fmo, [False, False, False, False, True, True], 2, "H2-3"),
]

fmo.run(fragments)
print("# GAMESS:       -3.2834656457999998")
