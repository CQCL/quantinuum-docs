r"""A AlgorithmMcLachlanRealTime time evolution simulation"""

# imports
import numpy as np

from pytket.extensions.qiskit import AerStateBackend

from sympy import Symbol, I

from inquanto.algorithms.time_evolution import (
    AlgorithmMcLachlanRealTime,
)
from inquanto.computables.atomic import ExpectationValue
from inquanto.computables.primitive import ComputableNDArray
from inquanto.minimizers import NaiveEulerIntegrator
from inquanto.operators import FermionOperator
from inquanto.protocols import (
    SparseStatevectorProtocol,
)
from inquanto.spaces import FermionSpace
from inquanto.states import QubitState

# For this example, we'll propagate a Hubbard dimer in real time and examine how the electrons move from the initial state.

# We define a plotting function for the energy and orbital occupiation numbers of the system
def plotting(time_span, evs, solution, symbols, name, title):
    from matplotlib import pyplot as plt

    fig = plt.figure(figsize=(4, 8))

    (ax0, ax1, ax2, ax3) = fig.subplots(4, 1)

    fig.suptitle(f"{title}\n{name}")
    ax0.plot(time_span, solution, label=symbols)
    ax1.plot(time_span, evs[:, 2:], label="occupation")
    ax2.plot(time_span, evs[:, 0], label="energy")
    ax3.plot(time_span, evs[:, 1], label="total particle")

    ax0.legend()

    ax0.set_ylabel(r"Ansatz parameters")
    ax1.set_ylabel("Occupation number\n(spin orbital)")
    ax2.set_ylabel(r"Total energy ($Ha$)")
    ax3.set_ylabel(r"Total number of particle")
    ax3.set_xlabel(r"time ($\hbar/Ha$)")

    fig.tight_layout()
    fig.savefig(f"figure_{title}_{name}.png")

    plt.show()


# We manually construct our Hubbard dimer operators using this method, which returns our
# Hamiltonian (needed for time evolution) as well as the number operators we use to measure
# orbital occupancies during time evolution.
def build_operators():
    fock_space = FermionSpace(4)

    n1u = FermionOperator(((fock_space.index(0, 0), 1), (fock_space.index(0, 0), 0)))
    n1d = FermionOperator(((fock_space.index(0, 1), 1), (fock_space.index(0, 1), 0)))
    n2u = FermionOperator(((fock_space.index(1, 0), 1), (fock_space.index(1, 0), 0)))
    n2d = FermionOperator(((fock_space.index(1, 1), 1), (fock_space.index(1, 1), 0)))

    cc21u = FermionOperator(((fock_space.index(1, 0), 1), (fock_space.index(0, 0), 0)))
    cc12u = FermionOperator(((fock_space.index(0, 0), 1), (fock_space.index(1, 0), 0)))
    cc21d = FermionOperator(((fock_space.index(1, 1), 1), (fock_space.index(0, 1), 0)))
    cc12d = FermionOperator(((fock_space.index(0, 1), 1), (fock_space.index(1, 1), 0)))

    hamiltonian_operator = (
        -1 * (cc21u + cc12u + cc21d + cc12d)
        + 4 * (n1u * n1d + n2u * n2d)
        + 0 * (n1u + n1d)
    )

    qubit_orbital_number_operators = [
        op.qubit_encode() for op in fock_space.construct_orbital_number_operators()
    ]

    return (
        hamiltonian_operator.qubit_encode(),
        fock_space.construct_number_operator().qubit_encode(),
        *qubit_orbital_number_operators,
    )


# Hamiltonian and number operators returned by the method defined above
hamiltonian, *operators = build_operators()

# Prepare an ansatz manually using a linear combination of qubit states
# which have custom coefficients.
from sympy import sin, cos, exp

theta = Symbol("theta0")
phi = Symbol("phi0")
gamma = Symbol("gamma0")
phase0 = Symbol("phase0")
phase1 = Symbol("phase1")
phase2 = Symbol("phase2")
phase3 = Symbol("phase3")

c0 = sin(phi) * cos(theta) * exp(I * phase0)
c1 = sin(phi) * sin(theta) * cos(gamma) * exp(I * phase1)
c2 = sin(phi) * sin(theta) * sin(gamma) * exp(I * phase2)
c3 = cos(phi) * exp(I * phase3)

ansatz = (
    QubitState([1, 1, 0, 0], c0)
    + QubitState([1, 0, 0, 1], c3)
    + QubitState([0, 1, 1, 0], c2)
    + QubitState([0, 0, 1, 1], c1)
)

# Get a set of initial ansatz symbols
initial = ansatz.state_symbols.construct_random(seed=0, mu=0, sigma=0.01)

time = np.linspace(0, 2, 201)
# Construct a numerical integrator which will define the state at time t+1 using the computables
integrator = NaiveEulerIntegrator(
    time, disp=True, linear_solver=NaiveEulerIntegrator.linear_solver_scipy_pinvh
)

# Instantiate the variational time evolution class using the integrator, hamiltonian and state
algodeint = AlgorithmMcLachlanRealTime(
    integrator,
    hamiltonian,
    ansatz,
    initial_parameters=initial,
)

# Specify the protocols that evaluate the metric Tensor and Derivative computables
protocol = SparseStatevectorProtocol(AerStateBackend())

algodeint.build(protocol=protocol)

solution = algodeint.run()


# After the evolution run, we can measure/evaluate quantities at each time step:
exp_val_array = np.asarray(
    [ExpectationValue(ansatz, op) for op in [hamiltonian, *operators]]
)
evs_exp_runner = protocol.get_runner(ComputableNDArray(exp_val_array))

evs = algodeint.post_propagation_evaluation(evs_exp_runner)
evs = np.asarray(evs)

# These figures show the orbital occupancy dynamics from the initial 1001 state.
# Due to numerics in the state definition we observe some drift in the system total energy,
# which should be conserved.
plotting(
    time,
    evs,
    solution,
    ansatz.state_symbols,
    "AlgorithmMcLachlanRealTime",
    "hubbard_dimer",
)
