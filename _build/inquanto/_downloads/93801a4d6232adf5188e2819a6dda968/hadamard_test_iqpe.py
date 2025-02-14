r"""Demonstration of the generation of IPEA circuits, and their use for Hadamard test sampling."""

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


from pytket.circuit import (
    Circuit,
    OpType,
)
from pytket.extensions.qiskit import AerBackend
from pytket.circuit.display import render_circuit_jupyter

from inquanto.protocols import IterativePhaseEstimation

###
# Computational setup.

# Number of shots for each circuit.
n_shots = 100000

# Backend setting.
backend = AerBackend()

###
# Target system setup.

# Prepare a random phase to be used in Ctrl-U construction
# e0 = 2 * np.random.random()
e0 = 1.198059919365895


### Circuit preparation
# Define simple method to obtain Ctrl-U circuit gadget.
def get_ctrlu(k: int):
    circ = Circuit(2)
    for _ in range(k):
        circ.add_gate(OpType.CU1, e0, (0, 1))
    return circ


# we can instance the
ctrlu = get_ctrlu(k=1)

# State preparation circuit.
state = Circuit(1).X(0)

###
# instance IQPE protocol
protocol = IterativePhaseEstimation(
    backend=backend,
    n_shots=n_shots,
    optimisation_level=0,
)

# build IQPE circuits with the state and function to build ctrl-u circuits
protocol.build_from_circuit(
    state=state,
    get_ctrlu=get_ctrlu,
)

# iqpe has a method for rebuilding the circuits for the
# set k and beta (repeats of unitary and ancilla rotation respectively)

# we can use this method to examine the effect of these variables on
# our circuit
# render_circuit_jupyter(protocol.update_k_and_beta(k=2,beta=-0.5).get_circuits()[0])


def measure_function(k: int, beta: float) -> Circuit:
    protocol.update_k_and_beta(k=k, beta=beta)
    # Performs the Hadamard test
    protocol.run(seed=0)
    meas_outcome = protocol.get_measurement_outcome()
    return meas_outcome


###
# use the measure_function to prepare and run circuits for a range of k and beta
ms = [measure_function(k=1, beta=beta) for beta in (0.0, -0.5)]

###
# analyze outputs
pcos, psin = [(m.count(0) - m.count(1)) / n_shots for m in ms]
phase = (np.arctan2(psin, pcos) / np.pi) % 2.0
estimate = phase
print(f"P_cos, P_sin     = {pcos:.4f}, {psin:.4f}")
print(f"Energy estimate  = {estimate:.5f} hartree")
print(f"Reference energy = {e0:.5f} hartree")
