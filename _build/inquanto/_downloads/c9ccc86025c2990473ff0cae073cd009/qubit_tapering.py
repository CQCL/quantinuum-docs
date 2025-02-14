r"""Qubit tapering - operators and Ansatzae."""


# imports
from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
from inquanto.express import load_h5
from inquanto.mappings import QubitMappingJordanWigner
from inquanto.spaces import FermionSpace, QubitSpace
from inquanto.states import FermionState
from inquanto.symmetry import PointGroup, TapererZ2

# Load the fermionic Hamiltonian, define HF state and map to qubits
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian_operator = h2.hamiltonian_operator.to_FermionOperator()
fermion_space = FermionSpace(4)
hf_state = FermionState([1, 1, 0, 0])
qubit_space = QubitSpace(4)
qubit_hamiltonian = QubitMappingJordanWigner.operator_map(hamiltonian_operator)
qubit_hf_state = QubitMappingJordanWigner.state_map(hf_state)

# Generate the symmetry operators from the Hamiltonian and find the symmetry sector of the HF state
symmetry_operators = qubit_space.symmetry_operators_z2(qubit_hamiltonian)
symmetry_sector = [x.symmetry_sector(qubit_hf_state) for x in symmetry_operators]

# We generate a TapererZ2 object, providing it information regarding the symmetry operator and symmetry sector.
taperer = TapererZ2(symmetry_operators, symmetry_sector)

# Now we can taper the Hamiltonian - note that three qubits have been tapered off.
tapered_hamiltonian = taperer.tapered_operator(qubit_hamiltonian)
print("Original Hamiltonian: {}".format(qubit_hamiltonian))
print("Tapered Hamiltonian: {}".format(tapered_hamiltonian))

# We can also optionally relabel the qubits in our tapered Hamiltonian
tapered_hamiltonian = taperer.tapered_operator(qubit_hamiltonian, relabel_qubits=True)
print("Tapered Hamiltonian: {}".format(tapered_hamiltonian))

# We can additionally generate a taperered Ansatz.  The behavior of how to deal with symmetry-breaking excitations can be controlled.  By default,
# each excitation will be checked, and an exception will be thrown if a symmetry-violating excitation is found:

ansatz_untapered = FermionSpaceAnsatzUCCSD(fermion_space, hf_state)

try:
    _ = FermionSpaceAnsatzUCCSD(fermion_space, hf_state, taperer=taperer)
except ValueError:
    print("This doesn't work because our Ansatz has symmetry breaking excitations!")

# However, we can instead discard them:
# InQuanto will warn the user
ansatz_tapered_discarding = FermionSpaceAnsatzUCCSD(
    fermion_space,
    hf_state,
    taperer=taperer,
    tapering_exponent_check_behavior="discard",
)

print("#### UNTAPERED ANSATZ REPORT ####")
print(ansatz_untapered.generate_report())
print("\n#### TAPERED ANSATZ REPORT, SYMMETRY VIOLATING EXCITATIONS DISCARDED ####")
print(ansatz_tapered_discarding.generate_report())

# Alternatively, if we are confident that we are not generating any symmetry-violating excitations (for instance, by using the symmetry filtering
# of FermionSpaceAnsatzUCCSD), we can skip the (relatively slow) validation entirely:

symmetrized_space = fermion_space = FermionSpace(
    4, point_group=PointGroup("D2h"), orb_irreps=["Ag", "Ag", "B1u", "B1u"]
)

ansatz_tapered_skipping = FermionSpaceAnsatzUCCSD(
    fermion_space,
    hf_state,
    taperer=taperer,
    tapering_exponent_check_behavior="skip",
)

print("\n#### TAPERED ANSATZ REPORT, SYMMETRY VALIDATION SKIPPED ####")
print(ansatz_tapered_skipping.generate_report())
