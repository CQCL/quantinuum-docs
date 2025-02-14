r"""An example showing how to use quantum computables."""

# Quantum computables are objects that may be evaluated via a quantum device or simulator.
# The most basic one as a simple integer.
from inquanto.computables.primitive import ComputableInt

qcint = ComputableInt(2)
print(qcint)

# It is so basic, there is no need a quantum device to evaluate.
print(qcint.evaluate())

# There are more general datastructures, such as list, and tuples
from inquanto.computables.primitive import ComputableTuple, ComputableList

qctuple = ComputableTuple(
    ComputableInt(2), ComputableList([ComputableInt(1), ComputableInt(0)]), -1
)
print(qctuple)

# At evaluation, any objects that is a quantum computable the .evaluate() method is called, recursively.
print(qctuple.evaluate())

# The quantum computables has a children method to check what children computables they contain
print(list(qctuple.children()))

# or can print the tree of computables:
qctuple.print_tree()

# and we can walk over the computable tree nodes:
for qc in qctuple.walk():
    print(qc)

# can build a custom computable:
from inquanto.computables.primitive import ComputableNode


class MyQC(ComputableNode):
    def __init__(self, value):
        self.value = value

    def evaluate(self, evaluator):
        return evaluator(self)


qc = ComputableTuple(ComputableInt(2), 3, MyQC("value"))

# and we can pass an evaluator,that in a quantum computing context could be some device measurement results.
print(qc.evaluate(evaluator=lambda v: v.value + "_evaluated"))

# If there are different computables, the same evaluator (node visitor) will be applied.
class MyQC2(ComputableNode):
    def __init__(self, value):
        self.value = value

    def evaluate(self, evaluator):
        return evaluator(self)


qc = ComputableTuple(qc, MyQC2("value2"))
print(qc.evaluate(evaluator=lambda v: v.value + "_evaluated"))


# If the two computables require different evaluations, a more general evaluator is required, for example:
def my_evaluator(node):
    if isinstance(node, MyQC):
        return node.value + "_evaluated"
    elif isinstance(node, MyQC2):
        return node.value + "_evaluated_differently"


print(qc.evaluate(evaluator=my_evaluator))

# or even more advanced evaluators:
from functools import singledispatchmethod


class MyEvaluator:
    @singledispatchmethod
    def __call__(self, node):
        raise NotImplementedError(f"{node} does not have evaluator")

    @__call__.register(MyQC)
    def _(self, node):
        return node.value + "_evaluated_in_class"

    @__call__.register(MyQC2)
    def _(self, node):
        return node.value + "_evaluated_differently_in_class"


print(qc.evaluate(evaluator=MyEvaluator()))

# Partial evaluation is also possible if the evaluator forbids it, for example:
class MyPartialEvaluator:
    @singledispatchmethod
    def __call__(self, node):
        return node

    @__call__.register(MyQC)
    def _(self, node):
        return node.value + "_evaluated_in_class"


print(qc.evaluate(evaluator=MyPartialEvaluator()))
# but note the return value in case of partial evaluation is still a computable

# That is
print(type(qc.evaluate(evaluator=MyPartialEvaluator())))
print(type(qc.evaluate(evaluator=MyEvaluator())))

# therefore multiple, different kinds of evaluations can be applied
qc_partial = qc.evaluate(evaluator=MyPartialEvaluator())
print(qc_partial.evaluate(evaluator=MyEvaluator()))


# More complicated computables can be built
from inquanto.computables.primitive import ComputableNDArray, ComputableFunction

qc = ComputableFunction(lambda x, y: f"{x}_{y}", MyQC("one"), MyQC2("two"))
print(qc.evaluate(evaluator=MyEvaluator()))
