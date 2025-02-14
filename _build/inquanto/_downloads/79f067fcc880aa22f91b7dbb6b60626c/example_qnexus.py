r"""Example using a simple ProjectiveMeasurements protocol with the qnexus API."""

# imports
import math
from datetime import datetime

from qnexus import AerConfig
from qnexus.client import auth, projects

from inquanto.extensions.nexus import ProtocolAnnotations
from inquanto.ansatzes import MultiConfigurationStateBox
from inquanto.protocols import ProjectiveMeasurements
from inquanto.states import QubitState, QubitStateString

# --------------
lc_qs = (
    QubitState(QubitStateString((0, 0, 0)), -math.sqrt(0.15))
    + QubitState(QubitStateString((0, 0, 1)), math.sqrt(0.20))
    + QubitState(QubitStateString((0, 1, 0)), math.sqrt(0.05))
    + QubitState(QubitStateString((0, 1, 1)), math.sqrt(0.10))
    + QubitState(QubitStateString((1, 0, 0)), math.sqrt(0.25))
    + QubitState(QubitStateString((1, 1, 0)), math.sqrt(0.25))
)

lc_ansatz = MultiConfigurationStateBox(lc_qs)

auth.login()

project_ref = projects.create(
    name=f"qNexus Demo {datetime.now()}", description="a demo project", properties={}
)

projects.add_property(
    project=project_ref,
    name="Number of Qubits",
    property_type="int",
    description="Number of qubits in my InQuanto algorithm",
    required=False,
)

backend_target = AerConfig()
protocol = ProjectiveMeasurements(
    backend=backend_target, shots_per_circuit=2, project_ref=project_ref
)
protocol.build({}, lc_ansatz)

circuit_annotations = ProtocolAnnotations(
    name="My Circuit",
    description="Description of my circuit",
    properties={"Number of Qubits": 3},
)

compile_job_annotations = ProtocolAnnotations(name=f"Compile Job {datetime.now()}")

protocol.compile_circuits(
    circuit_annotations=circuit_annotations,
    compile_job_annotations=compile_job_annotations,
)

execute_job_annotations = ProtocolAnnotations(name=f"Execute Job {datetime.now()}")

protocol.run(seed=0, execute_job_annotations=execute_job_annotations)

dominant_states = protocol.get_dominant_basis_states(n=2)
print(dominant_states)
