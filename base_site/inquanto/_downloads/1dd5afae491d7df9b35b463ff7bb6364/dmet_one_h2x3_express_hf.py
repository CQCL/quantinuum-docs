r"""One-shot DMET calculations on hydrogen rings."""

# imports
import numpy as np

from inquanto.express import run_rhf
from inquanto.embeddings import DMETRHF, DMETRHFFragmentDirect
from inquanto.express import load_h5
from inquanto.operators import ChemistryRestrictedIntegralOperator


# we create a bespoke class from DMETRHFFragmentDirect return the HF energy and reduced density matrices of a fragment of our system
class MyFragment(DMETRHFFragmentDirect):
    def solve(
        self,
        hamiltonian_operator: ChemistryRestrictedIntegralOperator,
        fragment_energy_operator: ChemistryRestrictedIntegralOperator,
        n_electron: int,
    ):
        energy, _, _, rdm1 = run_rhf(
            hamiltonian_operator, n_electron, conv=1e-12, maxit=100
        )

        fragment_energy = fragment_energy_operator.energy(rdm1)

        return energy, fragment_energy, rdm1


# we obtain a model system from inquanto.express and examine it
h2_3_ring_sto3g = load_h5("h2_3_ring_sto3g.h5", as_tuple=True)

print("HF energy (ref):  ", h2_3_ring_sto3g.energy_hf)
print(
    "HF energy (trace):",
    h2_3_ring_sto3g.hamiltonian_operator_lowdin.energy(
        h2_3_ring_sto3g.one_body_rdm_hf_lowdin
    ),
)

# define dmet solver
dmet = DMETRHF(
    h2_3_ring_sto3g.hamiltonian_operator_lowdin,
    h2_3_ring_sto3g.one_body_rdm_hf_lowdin,
    newton_tol=1e-13,
    newton_maxiter=100,
    occupation_atol=1e-6,
)

# The boolean mask array marks with True the spatial orbitals that define the fragment
fr1 = MyFragment(dmet, np.array([True, True, False, False, False, False]), "H2-1")
fr2 = MyFragment(dmet, np.array([False, False, True, True, False, False]), "H2-2")
fr3 = MyFragment(dmet, np.array([False, False, False, False, True, True]), "H2-3")

fragments = [fr1, fr2, fr3]

# this will perform one-shot dmet.
# the method requires a second argument, the fragment correlation pattern for full self consistent dmet
# see 'dmet_full_h2x3_express_hf.py' for example pattern construction
energy, chemical_potential, parameters = dmet.run(fragments)

print("# MY OUTPUT:")
print(f"# FINAL ENERGY:             {energy}")
print(f"# FINAL CHEMICAL POTENTIAL: {chemical_potential}")
print(f"# FINAL PARAMETERS:         {parameters}")

# FINAL ENERGY: -3.205946648985952
# FINAL CHEMICAL POTENTIAL: 1.8346296648995926e-07
