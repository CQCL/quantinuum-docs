# Copyright 2019-2024 Quantinuum
#
# You may not use this file except in compliance with the Licence.
# You may obtain a copy of the Licence in the LICENCE file accompanying
# these documents or at:
#
#     https://cqcl.github.io/inquanto/build/html/licence.html

r"""Test of NEVPT2 using RDMs from VQE
"""

import numpy
from inquanto.ansatzes import FermionSpaceAnsatzChemicallyAwareUCCSD
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.computables.composite import (
    RDM1234RealComputable,
    PDM1234RealComputable,
    get_rdm4_approx_conv,
)
from inquanto.spaces import FermionSpace
from inquanto.spaces import QubitSpace
from inquanto.states import FermionState
from pytket.extensions.qiskit import AerStateBackend

cas_elec = 2
cas_orbs = 4
qubit_hamiltonian = load_h5(
    "h2_631g_symmetry.h5", as_tuple=True
).hamiltonian_operator.qubit_encode()
space = FermionSpace(
    8,
    point_group="D2h",
    orb_irreps=numpy.asarray(["Ag", "Ag", "B1u", "B1u", "Ag", "Ag", "B1u", "B1u"]),
)

ansatz = FermionSpaceAnsatzChemicallyAwareUCCSD(
    fermion_space=space, fermion_state=FermionState([1, 1, 0, 0, 0, 0, 0, 0])
)

qubit_space = QubitSpace(space.n_spin_orb)
symmetry_operators = qubit_space.symmetry_operators_z2(qubit_hamiltonian)

backend = AerStateBackend()

protocol = SparseStatevectorProtocol(backend)

vqe_final_parameters = {
    "s0": -1.5618587839531388,
    "s1": -1.561886763292922,
    "d0": 0.07384698495558562,
    "d1": -0.5911167824931471,
    "d2": -1.4785191658655163,
    "d3": -0.736855031295867,
    "d4": 0.537546526677554,
}

mapping = QubitMappingJordanWigner()
computable = PDM1234RealComputable(
    space,
    ansatz,
    mapping,
    symmetry_operators,
    cas_elec,
    cas_orbs,
)
runner = protocol.get_runner(computable)
pdm1, pdm2, pdm3, pdm4 = runner(vqe_final_parameters)
# computable.set_trivial_evaluation(False)
# computable.build(protocol)
# computable.run(vqe_final_parameters)
# pdm1, pdm2, pdm3, pdm4 = computable.evaluate(vqe_final_parameters)

assert numpy.isclose(numpy.linalg.norm(pdm1), 1.97235934553679)
assert numpy.isclose(numpy.linalg.norm(pdm2), 5.228882128257982)
assert numpy.isclose(numpy.linalg.norm(pdm3), 14.284510832407866)
assert numpy.isclose(numpy.linalg.norm(pdm4), 40.30240063488914)

computable = RDM1234RealComputable(
    space,
    ansatz,
    mapping,
    symmetry_operators,
    cas_elec,
    cas_orbs,
)
runner = protocol.get_runner(computable)
rdm1, rdm2, rdm3, rdm4 = runner(vqe_final_parameters)
# computable.build(protocol)
# computable.run(vqe_final_parameters)
# rdm1, rdm2, rdm3, rdm4 = computable.evaluate(vqe_final_parameters)

assert numpy.isclose(numpy.linalg.norm(rdm1), 1.97235934553679)
assert numpy.isclose(numpy.linalg.norm(rdm2), 1.9999999966355002)
assert numpy.isclose(numpy.linalg.norm(rdm3), 0.0)
assert numpy.isclose(numpy.linalg.norm(rdm4), 0.0)

approx_rdm4 = get_rdm4_approx_conv(rdm1, rdm2, rdm3)

assert numpy.isclose(numpy.linalg.norm(approx_rdm4), 0.033917624541908370443)
