r"""Bayesian QPE protocol for noiseless backends"""
import numpy as np
from pytket.circuit import (
    Circuit,
    Pauli,
    PauliExpBox,
)
import phayes
from pytket.extensions.qiskit import AerBackend
from pytket.circuit.display import render_circuit_jupyter
from inquanto.protocols import (
    IterativePhaseEstimation,
)
from inquanto.operators import QubitOperator
from inquanto.ansatzes import CircuitAnsatz
from inquanto.extensions.phayes import AlgorithmBayesianQPE


# ### Input data


# Qubit operator.
# Two-qubit H2 with the equilibrium geometry.
qop = QubitOperator.from_string(
    "(-0.398, Z0), (-0.398, Z1), (-0.1809, Y0 Y1)",
)
qop_totally_commuting = QubitOperator.from_string(
    "(0.0112, Z0 Z1), (-0.3322, )",
)
fci_energy = np.linalg.eigh(
    (qop + qop_totally_commuting).to_sparse_matrix(qubits=2).todense()
)[0][0]
print(qop.df())
print(qop_totally_commuting.df())
print(f"FCI energy = {fci_energy:.5f} hartree")


# Parameters for constructing a function to return controlled unitary.
time = 0.1
n_trotter = 1
evo_ope_exp = qop.trotterize(trotter_number=n_trotter) * time
eoe_tot_com = qop_totally_commuting.trotterize(trotter_number=n_trotter) * time


# State preparation circuit.
state = Circuit(2)
state.add_pauliexpbox(
    PauliExpBox([Pauli.Y, Pauli.X], -0.07113),
    state.qubits,
)
render_circuit_jupyter(state)
ansatz = CircuitAnsatz(state)


backend = AerBackend()


# Construct the protocol object
protocol = IterativePhaseEstimation(backend=backend, optimisation_level=1).build(
    state=ansatz,
    evolution_operator_exponents=evo_ope_exp,
    eoe_totally_commuting=eoe_tot_com,
)


# ### Run the Stochastic QPE algorithm


phase_state = phayes.init(J=2000)

# Execute Bayesian QPE (modest setting to prioritize the speed).
verbose = 1
k_max = 300
n_updates = 50
conv = 3e-4


# Prepare the algorithm.
algorithm = AlgorithmBayesianQPE(
    phayes_state=phase_state,
    k_max=k_max,
    verbose=verbose,
).build(
    protocol=protocol,
)


circ = protocol.update_k_and_beta(k=1, beta=0.5).get_circuits()
render_circuit_jupyter(circ[0])


# Run the algorithm.
for i in range(n_updates):
    handles_mapping = algorithm.run_async()
    algorithm.join(handles_mapping)
    mu, sigma = algorithm.final_value()
    print(f"i={i} mu={mu:10.6f} sigma={sigma:10.6f}")
    if sigma < conv:
        break


# ### Analyze the results


# Show the result.
mu, sigma = algorithm.final_value()
energy_mu = -mu / time
energy_sigma = sigma / time
print(f"Energy(mu)    = {energy_mu:10.6f} hartree")
print(f"Energy(sigma) = {energy_sigma:10.6f} hartree")
print(f"FCI energy =    {fci_energy:10.6f} hartree")
