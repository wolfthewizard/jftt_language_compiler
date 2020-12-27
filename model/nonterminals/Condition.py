from model.nonterminals import Value


class Condition:

    def __init__(self, val1: Value, val2: Value, comparison: str):
        self.val1 = val1
        self.val2 = val2
        self.comparison = comparison

    def __str__(self):
        return "{} {} {}".format(self.val1, self.comparison, self.val2)

    def __repr__(self):
        return str(self)
