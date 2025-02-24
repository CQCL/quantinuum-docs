r"""Example inquanto-nglview visualization of periodic systems"""
from inquanto.extensions.nglview import VisualizerNGL
from inquanto.geometries import GeometryPeriodic
import nglview as nv
import numpy as np
from inquanto.extensions.pyscf import ChemistryDriverPySCFMolecularRHF

# AlB2 unit cell
a = 3.01  # lattice vectors in Angstroms
c = 3.27
a, b, c = [
    np.array([a, 0, 0]),
    np.array([-a * np.cos(60 * np.pi / 180), a * np.sin(60 * np.pi / 180), 0]),
    np.array([0, 0, c]),
]
atoms = [
    ["Al", [0, 0, 0]],
    ["B", a / 3 + b * 2 / 3 + c / 2],
    ["B", a * 2 / 3 + b / 3 + c / 2],
]

alb2_geom = GeometryPeriodic(geometry=atoms, unit_cell=[a, b, c])

ngl_structure = VisualizerNGL(alb2_geom)
alb2 = ngl_structure.visualize_unit_cell(atom_labels="index")
alb2


# Diamond fcc, 2 x 2 x 1 supercell
d = 3.576

a, b, c = [
    np.array([0, d / 2, d / 2]),
    np.array([d / 2, 0, d / 2]),
    np.array([d / 2, d / 2, 0]),
]
atoms = [["C", [0, 0, 0]], ["C", a / 4 + b / 4 + c / 4]]

cfcc_geom = GeometryPeriodic(geometry=atoms, unit_cell=[a, b, c])
cfcc_geom.build_supercell([2, 2, 1])

ngl_structure = VisualizerNGL(cfcc_geom)
cfcc = ngl_structure.visualize_unit_cell()
cfcc

# Overlay orbital isosurfaces. (Note: This is a molecular HF calculation, not truly periodic.)


driver = ChemistryDriverPySCFMolecularRHF(geometry=cfcc_geom, charge=0, basis="STO-3G")
hf_obj, hf_energy = driver._run_hf()
co = driver.get_cube_orbitals()


ngl_structure.visualize_orbitals(co[15])
