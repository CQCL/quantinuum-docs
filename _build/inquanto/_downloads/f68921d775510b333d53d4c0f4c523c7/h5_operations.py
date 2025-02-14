r"""Built-in example molecular data."""
# To get started you without a driver one can load precomputed test systems,
# that includes: Hamiltonian and reference energies

from inquanto.express import list_h5, load_h5

# One can load data as a dictionary, for example for the LiH test system:
lih_sto3g_dict = load_h5("lih_sto3g.h5")

# Data available:
print(lih_sto3g_dict.keys())

# On can list all available test systems:
print(list_h5())

# Alternatively one can load data as named tuple:
lih_sto3g = load_h5("lih_sto3g.h5", as_tuple=True)

# Hamilton operator in canonical orbitals:
print(lih_sto3g.hamiltonian_operator)

# Hamiltonian operator in orthogonalized atomic orbitals (Lowdin)
print(lih_sto3g.hamiltonian_operator_lowdin)

# Hartree--Fock energy
print(lih_sto3g.energy_hf)

# FCI energy
print(lih_sto3g.energy_casci)

# CCSD energy
print(lih_sto3g.energy_ccsd)

# Another simple test system:
h2_3_ring_sto3g = load_h5("h2_3_ring_sto3g.h5", as_tuple=True)

# Hamiltonian operator in orthogonalized atomic orbitals (Lowdin)
print(h2_3_ring_sto3g.hamiltonian_operator_lowdin)

# Hartree--Fock one-body RDM in orthogonalized atomic orbitals (Lowdin)
print(h2_3_ring_sto3g.one_body_rdm_hf_lowdin)

# [[ 1.00000000e+00  9.05286707e-01 -1.24900090e-16 -2.49266577e-01  5.82867088e-16  3.43979870e-01]
# [ 9.05286707e-01  1.00000000e+00  3.43979870e-01 -5.98479599e-17 -2.49266577e-01  1.67921232e-15]
# [-1.05818132e-16  3.43979870e-01  1.00000000e+00  9.05286707e-01  5.84601811e-16 -2.49266577e-01]
# [-2.49266577e-01 -5.85469173e-17  9.05286707e-01  1.00000000e+00  3.43979870e-01  2.42167397e-15]
# [ 4.57966998e-16 -2.49266577e-01  5.77662918e-16  3.43979870e-01  1.00000000e+00  9.05286707e-01]
# [ 3.43979870e-01  1.64451786e-15 -2.49266577e-01  2.44249065e-15  9.05286707e-01  1.00000000e+00]]

# The mean-field energy can be computed with the one electron rdm:
print(
    h2_3_ring_sto3g.hamiltonian_operator_lowdin.energy(
        h2_3_ring_sto3g.one_body_rdm_hf_lowdin
    )
)
print(h2_3_ring_sto3g.energy_hf)


# One can run also a simple RHF calculations on the Lowdin Hamiltonian,
# note this is intended only for simple test calculations, larger system please use
# one of the extension drivers, such es inquanto-pyscf
from inquanto.core._scf import run_rhf

energy, orbital_energies, mo, dm = run_rhf(
    h2_3_ring_sto3g.hamiltonian_operator_lowdin, h2_3_ring_sto3g.n_electron
)
print(energy)
