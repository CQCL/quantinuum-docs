r"""Demonstration of the generation of IPEA circuits with the specialized Quantinuum protocols."""

# `IterativePhaseEstimation` class may be used for designing
# the user-defined iterative QPE algorithm.
# Here we demonstrate how to use this feature with the Hadamard test as an example.
#
# Although the Hadamard test is not a stochastic QPE algorithm,
# It uses the same type of circuit and thus suitable for the simplest demonstration of QPE circuit generation.
# We calculate the phase by
# $$
#   \phi = \mathrm{arg}[\langle \phi | e^{i\phi} | \phi \rangle]
# $$
# The real and the imaginary parts in the square bracket is evaluated
# by setting $\beta = 0$ and $\beta=-\frac{\pi}{2}$, respectively.

# imports
import numpy as np

from pytket.circuit import Circuit, OpType
from pytket.extensions.qiskit import AerBackend
from pytket.circuit.display import render_circuit_jupyter

from inquanto.operators import QubitOperator
from inquanto.ansatzes import CircuitAnsatz
from inquanto.protocols import (
    IterativePhaseEstimationQuantinuum,
    CircuitEncoderQuantinuum,
)

# Computational setup.

# Error detection encoding method.
encmet = CircuitEncoderQuantinuum.ICEBERG

# Number of shots for each circuit.
n_shots = 100000

# Backend setting.
# noisefree shots here
backend = AerBackend()

# Target system setup.

# Evolution operator exponents.
# e0 = 2 * np.random.random()
e0 = 1.198059919365895

# prepare state and evolution operator
ansatz = CircuitAnsatz(Circuit(0))

time = 0.5
eoe = QubitOperator("Z0", e0).trotterize() * time


### Construct the IterativePhaseEstimationQuantinuum protocol object.
# This protocol can be used with any shot based backend, but the encoding method
# is designed with noisy simulation on the H series devices accesible using
# from pytket.extensions.quantinuum import QuantinuumBackend
# backend = QuantinuumBackend(device_name="H1-1E")
protocol = IterativePhaseEstimationQuantinuum(
    backend=backend,
    n_shots=n_shots,
    optimisation_level=0,
)

# here we build the qpe circuits from the state and evolution exponents
# so that the encoding can be applied.
# in contrast, the other iqpe examples build_from_circuit for state and ctrl-u
protocol.build(
    encoding_method=encmet,
    state=ansatz,
    evolution_operator_exponents=eoe,
)


# We can inspect the circuits.
# render_circuit_jupyter(protocol.update_k_and_beta(k=2,beta=-0.5).get_circuits()[0])
print(
    "CNOT GATES: ",
    protocol.update_k_and_beta(k=2, beta=-0.5)
    .get_circuits()[0]
    .n_gates_of_type(OpType.CX),
)


### Perform the Hadamard test
def measure(k: int, beta: float) -> Circuit:
    protocol.update_k_and_beta(k=k, beta=beta)
    protocol.run()
    meas_outcome = protocol.get_measurement_outcome()
    return meas_outcome


###
# use the measure_function to prepare and run circuits for a range of k and beta
ms = [measure(k=1, beta=beta) for beta in (0.0, -0.5)]


pcos, psin = [(m.count(0) - m.count(1)) / n_shots for m in ms]
phase = (np.arctan2(psin, pcos) / np.pi) % 2.0
estimate = -phase / time
print(f"P_cos, P_sin     = {pcos:.4f}, {psin:.4f}")
print(f"Energy estimate  = {estimate:.5f} hartree")
print(f"Reference energy = {e0:.5f} hartree")
