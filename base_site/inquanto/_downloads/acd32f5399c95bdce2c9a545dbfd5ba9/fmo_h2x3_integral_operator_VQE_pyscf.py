r"""An example Fragment molecular orbital(FMO) simulation of a 3-dihydrogen chain with custom VQE fragment solver."""

# imports
import numpy as np

np.set_printoptions(linewidth=10000, precision=8, suppress=True)

from pytket.extensions.qiskit import AerStateBackend

from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.express import run_vqe

from inquanto.extensions.pyscf.fmo._pyscf_fragments import FMOFragmentPySCFActive
from inquanto.extensions.pyscf import ChemistryDriverPySCFMolecularRHF
from inquanto.extensions.pyscf.fmo import FMO

# we create a bespoke class from FMOFragmentPySCFActive which returns the
# fragment active space uccsd vqe energy
class MyFMOFragmentVQE(FMOFragmentPySCFActive):
    def solve_final_active(
        self, fermionic_operator, fermion_space, fermion_state
    ) -> float:

        qubit_hamiltonian = fermionic_operator.qubit_encode()
        ansatz = FermionSpaceAnsatzUCCSD(fermion_space, fermion_state)
        vqe = run_vqe(ansatz, qubit_hamiltonian, AerStateBackend())

        return vqe.final_value


# manually construct the fermionic system for h2 x 3
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

# instantiate the FMO class with the full system hamiltonian
fmo = FMO(full_integral_operator)

# prepare fragment list (monomers)
fragments = [
    MyFMOFragmentVQE(fmo, [True, True, False, False, False, False], 2, "H2-1"),
    MyFMOFragmentVQE(fmo, [False, False, True, True, False, False], 2, "H2-2"),
    MyFMOFragmentVQE(fmo, [False, False, False, False, True, True], 2, "H2-3"),
]

# iteratively run fragment energies (uccsd vqe) on each fragment and perform fmo
# embedding to connect
energy = fmo.run(fragments)
print("# GAMESS (CCSD fragments):       -3.3512756041999996")

print("FMO UCCSD VQE fragment energy: " + str(energy))
