r"""An example FMO simulation of a 3-dihydrogen chain with custom VQE fragment solver."""
import numpy

numpy.set_printoptions(linewidth=10000, precision=8, suppress=True)

from inquanto.extensions.pyscf.fmo import FMOFragmentPySCFActive
from inquanto.extensions.pyscf import (
    ChemistryDriverPySCFMolecularRHF,
)
from inquanto.extensions.pyscf.fmo import FMO
from inquanto.express import load_h5

from pytket.extensions.qiskit import AerStateBackend


class MyFMOFragmentVQE(FMOFragmentPySCFActive):
    def solve_final_active(
        self,
        hamiltonian_operator,
        fermion_space,
        fermion_state,
    ) -> float:
        from inquanto.ansatzes import FermionSpaceAnsatzUCCSD

        qubit_operator = hamiltonian_operator.qubit_encode()

        ansatz = FermionSpaceAnsatzUCCSD(fermion_space, fermion_state)

        from inquanto.express import run_vqe

        vqe = run_vqe(ansatz, hamiltonian_operator, AerStateBackend())

        return vqe.final_value


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
    MyFMOFragmentVQE(fmo, [True, True, False, False, False, False], 2, "H2-1"),
    MyFMOFragmentVQE(fmo, [False, False, True, True, False, False], 2, "H2-2"),
    MyFMOFragmentVQE(fmo, [False, False, False, False, True, True], 2, "H2-3"),
]

fmo.run(fragments)
print("# GAMESS:       -3.3512756041999996")
