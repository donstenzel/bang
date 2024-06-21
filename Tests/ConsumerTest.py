from Consumers.Consumer import Consume, ConsumeSuccess

# Unconditional Consumption
c = Consume(lambda collection, pos: ConsumeSuccess(collection[1:], collection[0], pos +1))

assert c("Test", 0) == ConsumeSuccess("est", "T", 1)