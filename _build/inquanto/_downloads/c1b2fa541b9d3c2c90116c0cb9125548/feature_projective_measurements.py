r"""Example using a simple ProjectiveMeasurements protocol."""

# imports
import math
from pytket.extensions.qiskit import AerBackend

from inquanto.ansatzes import MultiConfigurationStateBox, MultiConfigurationState
from inquanto.protocols import ProjectiveMeasurements
from inquanto.states import QubitState, QubitStateString

# create a qubit state which is a normalized linear combination (lc) of
# of qubit basis states.
# Note: in JW encoding the list of QSS represent different numbers of electrons
# and therefore this linear combinations does not represent a particle conserving state
lc_qs = (
    QubitState(QubitStateString((0, 0, 0)), -math.sqrt(0.15))
    + QubitState(QubitStateString((0, 0, 1)), math.sqrt(0.20))
    + QubitState(QubitStateString((0, 1, 0)), math.sqrt(0.05))
    + QubitState(QubitStateString((0, 1, 1)), math.sqrt(0.10))
    + QubitState(QubitStateString((1, 0, 0)), math.sqrt(0.25))
    + QubitState(QubitStateString((1, 1, 0)), math.sqrt(0.25))
)
print("Is the qubit state normalized? ", lc_qs.is_normalized())

# Prepare an StatePreparationBox which can prepare arbitrary states.
# The input qubit state occupations are converted to a numeric state
# and then a circuit gadget made to create that numeric state
lc_ansatz = MultiConfigurationStateBox(lc_qs)

# Warning: getting numeric representation is exponentially scaling
print("The state being measured:")
print(lc_ansatz.df_numeric({}))


# instantiate a shot based backend
backend = AerBackend()

# instance the protocol
protocol = ProjectiveMeasurements(backend, 100000)
# creates 1 measurement circuit which measure all qubits
protocol.build({}, lc_ansatz)
protocol.compile_circuits()
# use backend to get runs of the circuit
# shot report probability of computational basis states
protocol.run(seed=0)

# reports states and shot sounds
dominant_states = protocol.get_dominant_basis_states(n=2)
print("Get the state with the first two dominant amplitudes:")
print(dominant_states)

print("|000> state probability and uncertainty:")
print("P(|000>)", protocol.get_zero_state_probability())
print("v(|000>)", protocol.get_zero_state_uncertainty())

print("Measured probabilities:")
print(protocol.get_dataframe_basis_states(max_rows=8))


# we can use the results to guess and construct a new linear combination
# of the most dominant states
measured_phaseless_state = protocol.get_phaseless_qubit_state(n=3)
print(measured_phaseless_state.df())
print(
    "Is my new linear combination normalized?", measured_phaseless_state.is_normalized()
)
print(
    "Use basis state probabilities to build a new state and compute the overlap with the original state:"
)
print("Overlap between new LC and original", measured_phaseless_state.vdot(lc_qs))
# Note that phase information has been lost due to  probabilistic interpretation
