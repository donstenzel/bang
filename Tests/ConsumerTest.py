from Consumer import Consume, ConsumeError, ConsumeSuccess
from Consumers import predicate

# Unconditional Consumption
c = Consume(lambda collection, pos: ConsumeSuccess(collection[1:], collection[0], pos +1))

assert c("Test", 0) == ConsumeSuccess("est", "T", 1)