r"""Orbital transformation methods."""

# imports
import numpy

from inquanto.operators import OrbitalTransformer

# prepare an array of initial orbital coffecients
v = numpy.array([[1, 2], [3, 4]])
print("Initial vector")
print(v)
# prepare an array of orbital overlap coffecients
overlap = numpy.array([[1.0, 0.66314574], [0.66314574, 1.0]])

# instantiate the transformer class
ot = OrbitalTransformer()

# gram schmidt
v_gs = ot.gram_schmidt(v)
print("Gram-Schmidt")
print(v_gs)

# gram schmidt wrt overlap matrix
v_gs_ovl = ot.gram_schmidt(v, overlap=overlap)
print("Gram-Schmidt wrt overlap matrix")
print(v_gs_ovl)
# find closest orthonormal set
v_orth = ot.orthonormalize(v)
print("Closest orthonormal")
print(v_orth)

# find closest orthonormal set wrt overlap matrix
v_orth_ovl = ot.orthonormalize(v, overlap=overlap)
print("Closest orthonormal wrt overlap")
print(v_orth_ovl)

# find the unitary which relates two vectors/mo coefficient matrices
v2 = numpy.array([[2, 1], [4, 3]])
u = ot.compute_unitary(v_init=v, v_final=v2)
print("Unitary rotation matrix between 2 example vectors")
print(u)

# these rotations can be inputs for driver transf arguments
