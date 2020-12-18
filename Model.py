class Identifier:

    def __init__(self, name, offset):
        self.name = name
        self.offset = offset

    def __repr__(self):
        if not self.offset:
            return self.name
        else:
            return self.name + "(" + str(self.offset) + ")"


class OperationObject:

    def __init__(self, val1, val2, operation):
        self.val1 = val1
        self.val2 = val2
        self.operation = operation


class ConditionObject:

    def __init__(self, val1, val2, comparison):
        self.val1 = val1
        self.val2 = val2
        self.comparison = comparison
