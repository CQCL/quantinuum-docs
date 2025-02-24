r"""Preparation of a 6 qubit linear combination of fermionic occupation states with fixed coefficients."""

# imports
from math import sqrt

from pytket import OpType

from inquanto.ansatzes import (
    MultiConfigurationState,
)
from inquanto.states import FermionState, FermionStateString
from inquanto.mappings import QubitMappingJordanWigner

# the 4 determinant example from https://arxiv.org/pdf/2106.13839.pdf, using our general implementation,
# with normalized coefficients selected by user.
fss_ref, coeff_fss1 = FermionStateString([1, 1, 0, 0, 0, 0]), sqrt(1 / 2)  # c_1
fss_2, coeff_fss2 = FermionStateString([0, 0, 1, 1, 0, 0]), -sqrt(1 / 6)  # c_2
fss_3, coeff_fss3 = FermionStateString([0, 0, 0, 0, 1, 1]), sqrt(1 / 8)  # c_3
fss_4, coeff_fss4 = FermionStateString([1, 0, 0, 1, 0, 0]), sqrt(5 / 24)  # c_4
fock_states = FermionState(
    {fss_ref: coeff_fss1, fss_2: coeff_fss2, fss_3: coeff_fss3, fss_4: coeff_fss4}
)

fock_states = QubitMappingJordanWigner().state_map(fock_states)

# This multi configuration state is non-symbolic (i.e. should not be used alone in VQE)
multi_state = MultiConfigurationState(fock_states)

print("Ansatz report:\n", multi_state.generate_report())
print("Circuit resources:", multi_state.circuit_resources())
print("Dataframe of state vector:\n", multi_state.df_numeric())
