r"""Example of executing an inquanto protocol list with the qnexus API."""

from datetime import datetime

from inquanto.protocols import ProtocolList, PauliAveraging, HadamardTestOverlap
from inquanto.ansatzes import CircuitAnsatz
from inquanto.operators import QubitOperator

from qnexus.models import AerConfig
from qnexus.client import auth, projects

from pytket.circuit import Circuit

auth.login()

project_ref = projects.create(
    name=f"protocol list demo {datetime.now()}",
    description="a demo project",
    properties={},
)

projects.add_property(
    project=project_ref,
    name="Number of Qubits",
    property_type="int",
    description="Number of qubits in my InQuanto algorithm",
    required=False,
)

backend = AerConfig()

state1 = CircuitAnsatz(Circuit(4).X(0).X(1))
state2 = CircuitAnsatz(Circuit(4).X(2).X(3))

op = QubitOperator("Y0 X1 X2 X3")

protocols = ProtocolList()

protocol_pa = PauliAveraging(backend, project_ref=project_ref)
protocol_ho = HadamardTestOverlap(backend, 1000, project_ref=project_ref)

protocols.append(protocol_pa.build({}, state1, op))
protocols.append(protocol_ho.build({}, state1, state2, op, component="complex"))

_ = protocols.compile_circuits(compile_job_name=f"compile demo {datetime.now()}").run(
    seed=0
)

print(f"\nPauliAveraging protocol has been run: {protocol_pa.is_run}")
print(f"HadamardTestOverlap protocol has been run: {protocol_ho.is_run}")
