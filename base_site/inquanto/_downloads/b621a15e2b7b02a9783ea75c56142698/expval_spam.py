r"""Running PauliAveraging with inquanto's noise mitigation."""

# imports
from sympy import Symbol, pi

from pytket import Circuit

from inquanto.protocols import SPAM
from inquanto.express import get_noisy_backend
from inquanto.ansatzes import CircuitAnsatz
from inquanto.operators import QubitOperator
from inquanto.protocols import PauliAveraging

# create a simple symbolic pytket circuit
circ = Circuit(2)
circ.Ry(-2 * Symbol("a") / pi, 0)
circ.CX(0, 1)
circ.Rz(-2 * Symbol("b") / pi, 1)
circ.Rx(-2 * Symbol("c") / pi, 1)
circ.CX(1, 0)
circ.Ry(-2 * Symbol("d") / pi, 0)
# use the CircuitAnsatz to make an inquanto ansatz from the pytket circ
ansatz = CircuitAnsatz(circ)

# create a simple qubit operator
kernel = (
    QubitOperator("X0 X1", 2) + QubitOperator("Y0 Y1", 2) + QubitOperator("Z0 Z1", 2)
)
# create a dictionary with values for a,b,c,d in the ansatz
parameters = ansatz.state_symbols.construct_from_array([0.1, 0.2, 0.3, 0.4])

# get a simple noisy AerBackend for 2 qubits using the express method
# this has CNOT and Readout errors
backend = get_noisy_backend(2)

# instantiate protocol
protocol = PauliAveraging(backend, shots_per_circuit=10000)

# prepare state prep and measurement (SPAM) error mit class to apply to protocol runs
mitms_spam = SPAM(backend=backend).calibrate(calibration_shots=50, seed=0)

# build and run measurement circuits without SPAM
protocol.build(parameters, ansatz, kernel).compile_circuits().run(seed=0)
# evalaute energy using the noisy shots
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("Raw: ", energy_value)

protocol.clear()
# re-build and run measurement circuits including SPAM circuits
protocol.build(
    parameters, ansatz, kernel, noise_mitigation=mitms_spam
).compile_circuits().run(seed=0)
# evaluate energy using noisy shots with SPAM correction
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("NoiseMitigation (SPAM): ", energy_value)
