r"""One-shot DMET calculations on hydrogen rings"""

# imports
from typing import Tuple

import numpy as np

from pytket.extensions.qiskit import AerStateBackend

from inquanto.algorithms.vqe import AlgorithmVQE
from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.computables.composite import RestrictedOneBodyRDMRealComputable
from inquanto.computables.atomic import ExpectationValue, ExpectationValueDerivative
from inquanto.computables.primitive import ComputableTuple
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.minimizers import MinimizerScipy
from inquanto.protocols import SparseStatevectorProtocol
from inquanto.embeddings import DMETRHF, DMETRHFFragmentActive
from inquanto.express import load_h5
from inquanto.operators import ChemistryRestrictedIntegralOperator, RestrictedOneBodyRDM
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState

# we create a bespoke class from DMETRHFFragmentActive which reports UCCSD energy and reduced density matrices
# for an active space of a fragment of our system
class MyFragment(DMETRHFFragmentActive):
    def solve_active(
        self,
        hamiltonian_operator: ChemistryRestrictedIntegralOperator,
        fragment_energy_operator: ChemistryRestrictedIntegralOperator,
        fermion_space: FermionSpace,
        fermion_state: FermionState,
    ) -> Tuple[float, float, RestrictedOneBodyRDM]:

        jw = QubitMappingJordanWigner()
        ansatz = FermionSpaceAnsatzUCCSD(fermion_space, fermion_state, jw)

        h_op = jw.operator_map(hamiltonian_operator)
        e_op = jw.operator_map(fragment_energy_operator)

        objective_expression = ExpectationValue(ansatz, h_op)
        fragment_energy_expression = ExpectationValue(ansatz, e_op)
        # make a computable for the RDM needed for embedding
        vqe_rdm1_expression = RestrictedOneBodyRDMRealComputable(
            fermion_space, ansatz, jw
        )

        gradient_expression = ExpectationValueDerivative(
            ansatz, h_op, ansatz.state_symbols.symbols
        )

        vqe = AlgorithmVQE(
            objective_expression=objective_expression,
            minimizer=MinimizerScipy(),
            initial_parameters=ansatz.state_symbols.construct_random(0, 0.0, 0.01),
            # also evaluate the auxiliary expression for the RDM used in embedding
            auxiliary_expression=ComputableTuple(
                fragment_energy_expression, vqe_rdm1_expression
            ),
            gradient_expression=gradient_expression,
        )
        protocol = SparseStatevectorProtocol(AerStateBackend())
        vqe.build(protocol_objective=protocol, protocol_gradient=protocol)
        vqe.run()

        energy = vqe.final_value
        fragment_energy, vqe_rdm1 = vqe.final_evaluated_auxiliary_expression

        return energy, fragment_energy.real, vqe_rdm1


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
fr1 = MyFragment(
    dmet, np.array([True, True, False, False, False, False]), "H2-1", frozen=[0, 3]
)
fr2 = MyFragment(
    dmet, np.array([False, False, True, True, False, False]), "H2-2", frozen=[0, 3]
)
fr3 = MyFragment(
    dmet, np.array([False, False, False, False, True, True]), "H2-3", frozen=[0, 3]
)

fragments = [fr1, fr2, fr3]

# Perform one-shot (no correlation pattern) DMET on the fragmented system.
# All fragment RDMs here are given by the UCCSD VQE calculation.
# This will iteratively run the fragment solvers and solve the embedding problem.
energy, chemical_potential, parameters = dmet.run(fragments)

print("# MY OUTPUT:")
print(f"# FINAL ENERGY:             {energy}")
print(f"# FINAL CHEMICAL POTENTIAL: {chemical_potential}")
print(f"# FINAL PARAMETERS:         {parameters}")

# FINAL ENERGY:             -3.204040649963966
# FINAL CHEMICAL POTENTIAL: 1.824411210493936e-07
