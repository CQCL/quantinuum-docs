r"""Computable expression example (ExpectationValue)"""
# Computable expression example (ExpectationValue):
# A general way to convert familiar quantum chemistry expressions to measurement circuits.


# imports
from pytket.extensions.qiskit import AerBackend
from qiskit_aer.noise import NoiseModel, ReadoutError

from inquanto.ansatzes import FermionSpaceStateExpChemicallyAware
from inquanto.computables import ExpectationValue
from inquanto.express import load_h5
from inquanto.protocols import PauliAveraging
from inquanto.spaces import FermionSpace
from inquanto.states import FermionState
from inquanto.symmetry import PointGroup

# Construct a simple noise model using Qiskit tools
noise_model = NoiseModel()
pr = 0.1
n_qubits = 4
probabilities = [[1 - pr, pr], [pr, 1 - pr]]
# only readout error here
error = ReadoutError(probabilities)
for i in range(n_qubits):
    noise_model.add_readout_error(error, qubits=[i])


# express module to load an example system
h2 = load_h5("h2_sto3g.h5", as_tuple=True)
hamiltonian = h2.hamiltonian_operator
space = FermionSpace(
    4, point_group=PointGroup("D2h"), orb_irreps=["Ag", "Ag", "B1u", "B1u"]
)

state = FermionState([1, 1, 0, 0])
qubit_hamiltonian = hamiltonian.qubit_encode()

# construct ansatz and make a dictionary for setting parameters when executing circuit
exponents = space.construct_double_ucc_operators(state)
ansatz = FermionSpaceStateExpChemicallyAware(exponents, state)
params = ansatz.state_symbols.construct_from_array([-0.111])

# load the toy noise model into the
noisy_backend = AerBackend(noise_model=noise_model)

# construct computable
expectation = ExpectationValue(ansatz, hamiltonian.qubit_encode())
# expectation1 = ExpectationValue(ansatz, QubitOperator("X0 Y1 Y2 X3", 1.0))

protocol = PauliAveraging(noisy_backend, shots_per_circuit=8000)
protocol.build_from(params, expectation)
protocol.compile_circuits()
protocol.run()

# evaluate the computable using the results in the protocol
energy = expectation.evaluate(protocol.get_evaluator())
# energy will typically end up higher than the noise free shots
# modify the value for the readout error pr=0.1 to examine the influence of noise
print(f"Energy: {energy}")
