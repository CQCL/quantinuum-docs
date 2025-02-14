r"""Example inquanto-nglview visualization of molecular systems"""
from inquanto.extensions.nglview import VisualizerNGL
from inquanto.geometries import GeometryMolecular
from inquanto.extensions.pyscf import ChemistryDriverPySCFMolecularRHF


d = 0.982
a = 104.5

zmatrix = f"""
H
O 1 {d}
H 2 {d} 1 {a}
"""

geometry = GeometryMolecular(geometry=zmatrix)
ngl_structure = VisualizerNGL(geometry)
h2o = ngl_structure.visualize_molecule()
h2o

driver = ChemistryDriverPySCFMolecularRHF(geometry=geometry, charge=0, basis="STO-3G")
hf_obj, hf_energy = driver._run_hf()
co = driver.get_cube_orbitals()
ngl_mos = [ngl_structure.visualize_orbitals(c) for i, c in enumerate(co)]
ngl_mos[2]


image = ngl_mos[2].render_image(trim=True)
image


with open("h2o_mo.png", "wb") as fhandle:
    fhandle.write(image.value)
