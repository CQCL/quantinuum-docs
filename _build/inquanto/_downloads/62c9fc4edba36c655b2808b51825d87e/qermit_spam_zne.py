r"""Running protocols via Qermit's MitRes and MitEx."""
from pytket import Circuit
from qermit.spam import gen_UnCorrelated_SPAM_MitRes
from qermit.zero_noise_extrapolation import gen_ZNE_MitEx
from sympy import Symbol, pi

from inquanto.express import get_noisy_backend
from inquanto.ansatzes import CircuitAnsatz
from inquanto.operators import QubitOperator
from inquanto.protocols import PauliAveraging

circ = Circuit(2)
circ.Ry(-2 * Symbol("a") / pi, 0)
circ.CX(0, 1)
circ.Rz(-2 * Symbol("b") / pi, 1)
circ.Rx(-2 * Symbol("c") / pi, 1)
circ.CX(1, 0)
circ.Ry(-2 * Symbol("d") / pi, 0)
ansatz = CircuitAnsatz(circ)

kernel = (
    QubitOperator("X0 X1", 2) + QubitOperator("Y0 Y1", 2) + QubitOperator("Z0 Z1", 2)
)
parameters = ansatz.state_symbols.construct_from_array([0.1, 0.2, 0.3, 0.4])

backend = get_noisy_backend(2)
protocol = PauliAveraging(backend, shots_per_circuit=10000)
protocol.build(parameters, ansatz, kernel).compile_circuits()

uc_spam_mitres = gen_UnCorrelated_SPAM_MitRes(backend=backend, calibration_shots=50)
protocol.run_mitres(uc_spam_mitres, {})
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("MitRes (SPAM): ", energy_value)


zne_mitex = gen_ZNE_MitEx(backend=backend, noise_scaling_list=[3])
protocol.run_mitex(zne_mitex, {})
energy_value = protocol.evaluate_expectation_value(ansatz, kernel)
print("MitEx (ZNE3): ", energy_value)
print("Exact: ", 1.5196420749021882)
