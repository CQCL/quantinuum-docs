r"""Preparation of a 4 qubit linear combination of fermionic occupation states with fixed coefficients."""

# imports
from math import sqrt

from pytket import OpType

from inquanto.ansatzes import (
    MultiConfigurationStateBox,
)
from inquanto.states import FermionState, FermionStateString
from inquanto.mappings import QubitMappingJordanWigner

# # 6 basis states, 4 qubits
# we set our coefficients here so that the multiconfigstate will be normalized
fss_1, coeff_fss1 = FermionStateString([1, 1, 0, 0]), sqrt(1 / 6)
fss_2, coeff_fss2 = FermionStateString([1, 0, 0, 1]), -sqrt(1 / 6)
fss_3, coeff_fss3 = FermionStateString([0, 1, 1, 0]), sqrt(1 / 6)
fss_4, coeff_fss4 = FermionStateString([0, 0, 1, 1]), sqrt(1 / 6)
fss_5, coeff_fss5 = FermionStateString([1, 0, 1, 0]), -sqrt(1 / 6)
fss_6, coeff_fss6 = FermionStateString([0, 1, 0, 1]), sqrt(1 / 6)
fock_states = FermionState(
    {
        fss_1: coeff_fss1,
        fss_2: coeff_fss2,
        fss_3: coeff_fss3,
        fss_4: coeff_fss4,
        fss_5: coeff_fss5,
        fss_6: coeff_fss6,
    }
)

fock_states = QubitMappingJordanWigner().state_map(fock_states)
# This multi configuration state box is non-symbolic (i.e. should not be used alone in VQE)
# MultiConfigurationStateBox calls pytket's StatePreparationBox.
multi_state = MultiConfigurationStateBox(fock_states)
print(
    "\noperations on the circuit to get multiconfig state:\n",
    multi_state.state_circuit.get_commands(),
    "\n",
)
print("Ansatz report:\n", multi_state.generate_report())
print("Circuit resources:", multi_state.circuit_resources())
print("Dataframe of state vector:\n", multi_state.df_numeric())
