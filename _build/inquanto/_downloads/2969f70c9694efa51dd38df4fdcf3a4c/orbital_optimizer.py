r"""Orbital optimization using Pipek-Mezey as an example."""

# imports
import numpy

from inquanto.express import load_h5, run_rhf
from inquanto.minimizers import MinimizerScipy
from inquanto.operators import OrbitalOptimizer


# load an example system from express database
h2_3_ring_sto3g = load_h5("h2_3_ring_sto3g.h5", as_tuple=True)
# 12 spin-orbitals, 6 spatial


# construct the pipek-mezey cost function
def cost(mo: numpy.ndarray):
    aggregate = 0.0
    for p in projectors:
        aggregate += sum(numpy.dot(mo[:, p], mo[:, p].conj().T).diagonal() ** 2)
    return -aggregate


# get canonical orbitals as starting guess
total, orbital_energies, mo, dm = run_rhf(
    h2_3_ring_sto3g.hamiltonian_operator_lowdin,
    h2_3_ring_sto3g.n_electron,
    conv=1e-12,
    maxit=1000,
)
print("Shape of 3 x H2 HF MOs")
print(numpy.shape(mo))
print("3 x H2 HF RHF MO coefficients")
print(mo)

# projectors defining centers of basis functions
projectors = [
    numpy.array([True, False, False, False, False, False]),
    numpy.array([False, True, False, False, False, False]),
    numpy.array([False, False, True, False, False, False]),
    numpy.array([False, False, False, True, False, False]),
    numpy.array([False, False, False, False, True, False]),
    numpy.array([False, False, False, False, False, True]),
]

# construct OrbitalOptimizer object,
oo = OrbitalOptimizer(
    v_init=mo,  # initial orbitals
    functional=cost,  # function to be optimized
    minimizer=MinimizerScipy(
        "BFGS", options={"gtol": 1e-12}
    ),  # minimizer specification
    split_rotation=False,  # set this to true to avoid mixing virtual and occupied orbitals
    point_group=None,  # if point group information is provided, the optimizer will try to avoid breaking symmetries
    orbital_irreps=None,
    reduce_free_parameters=True,  # remove variables frozen to zero by problem specification to speed up the optimization
)

# begin the minimization from all zero initial variables
# returns the new MO coefficients
new_mo, unitary, cost_score = oo.optimize(random_initial_variables=False)
print("New PM localized MO shape ")
print(numpy.shape(new_mo))
print("3 x H2 HF RHF PM localized orbital coefficients")
print(new_mo)

# we can also obtain the same orbital rotation unitary from
# the optimizer using the transformer class
from inquanto.operators import OrbitalTransformer

rotation_u = OrbitalTransformer().compute_unitary(v_init=mo, v_final=new_mo)
print(numpy.allclose(unitary, rotation_u, atol=1e-06))

# oo() can also be used to return only the new mo coefficients for compatibility with driver transf arguments
