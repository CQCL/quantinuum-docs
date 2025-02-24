r"""An exact imaginary time evolution simulation using express methods"""

# imports
import numpy as np

from inquanto.express import DriverHubbardDimer, run_time_evolution
from inquanto.states import QubitState

# For this example, we'll propagate a Hubbard dimer in imaginary time and examine the relaxation of the system towards the ground state.
# Let's initialize the system so we can get the quantities we need for quantum simulation - a space, a state and a Hamiltonian.
driver = DriverHubbardDimer(t=1, u=4)
hamiltonian, space, state = driver.get_system()

# we can choose any initial state.
initial_state = QubitState([1, 0, 0, 1])

# now we can construct the operators we need using the space object, and map it to a qubit operator using the
# .qubit_encode().
qubit_number_operator = space.construct_number_operator().qubit_encode()
qubit_orbital_number_operators = [
    op.qubit_encode() for op in space.construct_orbital_number_operators()
]

qubit_hamiltonian = hamiltonian.qubit_encode()


# Now we can choose the points in time we wish to simulate. This can be done easily with np.linspace.
time_span = np.linspace(0, 5, 100)

# Using the run_time_evolution() convenience function and passing in the appropriate arguments, we can easily propagate
# the system.
qubit_states, evs = run_time_evolution(
    initial_state,
    time_span,
    qubit_hamiltonian,
    qubit_number_operator,
    *qubit_orbital_number_operators,
    n_qubits=4,
    real=False,
)

# Now we have our results, we can plot them using matplotlib.
from matplotlib import pyplot as plt

fig = plt.figure(figsize=(4, 6))

(ax1, ax2, ax3) = fig.subplots(3, 1)

fig.suptitle("Hubbard dimer, $t = 1Ha$, \n $U = 4Ha$ with initial state $|1001>$")
ax1.plot(time_span, evs[:, 2:], label="occupation")
ax2.plot(time_span, evs[:, 0], label="energy")
ax3.plot(time_span, evs[:, 1], label="total particle")

ax1.set_ylabel("Occupation number\n(spin orbital)")
ax2.set_ylabel(r"Total energy ($Ha$)")
ax3.set_ylabel(r"Total number of particle")
ax3.set_xlabel(r"time ($\hbar/Ha$)")

fig.tight_layout()
fig.savefig(f"figure_hubbard_dimer_imtime_evolution.png")

plt.show()
