r"""An example using dft projection based embedding of Pt5O2 with VQE."""
from pytket.extensions.qulacs import QulacsBackend
from inquanto.algorithms import AlgorithmVQE
from inquanto.ansatzes import FermionSpaceAnsatzChemicallyAwareUCCSD
from inquanto.computables import ExpectationValue
from inquanto.minimizers import MinimizerRotosolve
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.geometries import GeometryMolecular
from inquanto.extensions.nglview import VisualizerNGL
from inquanto.extensions.pyscf import (
    ChemistryDriverPySCFEmbeddingRHF,
    AVAS,
    FromActiveSpace,
)
from pyscf import gto, dft


# Pt5(O2) complex
# stretched O-O from 1.34 A to 1.60 A
pt5o2 = [
    ["Pt", [1.678586, 0.039578, 0.075135]],
    ["Pt", [-0.741409, 1.335153, -0.057106]],
    ["Pt", [-0.719302, -1.338673, -0.180241]],
    ["Pt", [0.023329, 0.009056, 2.045330]],
    ["Pt", [0.366370, 0.003414, -2.125032]],
    ["O", [-2.539206959, 0.779586773, -0.521797851]],
    ["O", [-2.585046041, -0.776506773, -0.152377149]],
]

g = GeometryMolecular(pt5o2)
visualizer = VisualizerNGL(g)
# visualizer.visualize_molecule()

mol = gto.Mole(
    atom=pt5o2,
    basis="def2-svp",
    ecp="def2-svp",
    verbose=3,
)
mol.build()
rks = dft.RKS(mol)
rks.xc = "b3lyp"
rks.kernel()


avas = AVAS(
    ["O 2p", "O 3p", "O 2s", "O 3s"], threshold=0.99, threshold_vir=0.9, verbose=4
)

# driver = ChemistryDriverPySCFEmbeddingRHF.from_mf(rks, transf=avas, frozen=avas.frozenf)
driver = ChemistryDriverPySCFEmbeddingRHF.from_mf(
    rks, transf=avas, frozen=FromActiveSpace(4, 4)
)

hamiltonian_operator, space, state = driver.get_system()

# orbital_cubes = driver.get_cube_orbitals()
# orbitals = [visualizer.visualize_orbitals(orb,red_isolevel=-2.0,
#                                          blue_isolevel=2.0) for orb in orbital_cubes]
# orbitals[0]

# remove non-hermitian part of hamiltonian due to numerical noise
qubit_hamiltonian = hamiltonian_operator.qubit_encode().hermitian_part()
ansatz = FermionSpaceAnsatzChemicallyAwareUCCSD(space, state)
print("Ansatz statistics, before pytket optimization")
print(ansatz.generate_report())


expectation_value = ExpectationValue(ansatz, qubit_hamiltonian)

vqe = (
    AlgorithmVQE(
        objective_expression=expectation_value,
        minimizer=MinimizerRotosolve(),
        initial_parameters=ansatz.state_symbols.construct_zeros(),
    )
    .build(
        protocol_objective=SparseStatevectorProtocol(backend=QulacsBackend()),
    )
    .run()
)

print(f"Minimum Energy: {vqe.generate_report()['final_value']} Ha")
print(
    f'VQE correction to HF: {vqe.generate_report()["final_value"]-driver.run_hf()} Ha'
)
