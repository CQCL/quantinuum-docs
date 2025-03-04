r"""Full DMET calculations on hydrogen rings."""

# imports
import numpy

from inquanto.express import run_rhf
from inquanto.embeddings import DMETRHF, DMETRHFFragment
from inquanto.express import load_h5
from inquanto.operators import ChemistryRestrictedIntegralOperator

# we create a bespoke class which returns the HF energy and reduced density matrices of a fragment of our system
class MyFragment(DMETRHFFragment):
    def solve(
        self, hamiltonian_operator: ChemistryRestrictedIntegralOperator, n_electron
    ):
        energy, _, _, rdm1_object = run_rhf(
            hamiltonian_operator, n_electron, conv=1e-12, maxit=100
        )

        rdm1 = rdm1_object._rdm1

        rdm2 = numpy.einsum("ij,kl->ijkl", rdm1, rdm1) - 0.5 * numpy.einsum(
            "il,kj->ijkl", rdm1, rdm1
        )

        return energy, rdm1, rdm2


# we obtain a model system from inquanto.express and examine it
h2_3_ring_sto3g = load_h5("h2_3_ring_sto3g.h5", as_tuple=True)

print("HF energy (ref):  ", h2_3_ring_sto3g.energy_hf)
print(
    "HF energy (trace):",
    h2_3_ring_sto3g.hamiltonian_operator_lowdin.energy(
        h2_3_ring_sto3g.one_body_rdm_hf_lowdin
    ),
)

# There will be two parameters in an array [u_0, u_1]
# with index 0 and 1 in the following pattern.
# The pattern to map that to a correlation potential matrix:
pattern = numpy.array(
    [
        [None, 0, None, None, None, None],
        [0, None, None, None, None, None],
        [None, None, None, 1, None, None],
        [None, None, 1, None, None, None],
        [None, None, None, None, None, 0],
        [None, None, None, None, 0, None],
    ]
)
# Note: due to symmetry we expect at the end of DMET u_0 = u_1, in principle we could have a single parameter, but
# let us see if DMET will converge to the expected correlation potential

# define dmet solver
dmet = DMETRHF(
    h2_3_ring_sto3g.hamiltonian_operator_lowdin,
    h2_3_ring_sto3g.one_body_rdm_hf_lowdin,
    newton_tol=1e-13,
    newton_maxiter=100,
)

# The boolean mask array marks with True the spatial orbitals that define the fragment
fr1 = MyFragment(dmet, numpy.array([True, True, False, False, False, False]), "H2-1")
fr2 = MyFragment(dmet, numpy.array([False, False, True, True, False, False]), "H2-2")
fr3 = MyFragment(dmet, numpy.array([False, False, False, False, True, True]), "H2-3")

# combine fragments
fragments = [fr1, fr2, fr3]

# this will iteratively run the fragment solvers and solve the embedding
# requires correlation potential matrix
energy, chemical_potential, parameters = dmet.run(fragments, pattern)

print("# MY OUTPUT:")
print(f"# FINAL ENERGY:             {energy}")
print(f"# FINAL CHEMICAL POTENTIAL: {chemical_potential}")
print(f"# FINAL PARAMETERS:         {parameters}")

# The result is expected to be close to the HF solution,
# as the fragment solver MySolver is an RHF solver.

# FINAL ENERGY:             -3.2059480022436073
# FINAL CHEMICAL POTENTIAL: -1.965765468463059e-07
# FINAL PARAMETERS:         [9.75176769e-06 9.74973611e-06]

# Due to symmetry of the ring, the parameters are also expected to be the same

# Note: with the inquanto-pyscf extension one can make for example a CCSD fragment solver
# This is considered an exercise the user is encouraged to make.
