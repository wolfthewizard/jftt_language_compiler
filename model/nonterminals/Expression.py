from model.nonterminals.Value import Value


class Expression:

    def __init__(self, val1: Value, val2: Value = None, operation: str = None):
        self.val1 = val1
        self.val2 = val2
        self.operation = operation

    def __str__(self):
        return "{} {} {}".format(self.val1, self.operation, self.val2)

    def __repr__(self):
        return str(self)

    def is_value(self):
        return self.val2 is None
