from model.nonterminals.Value import Value


class Write:

    def __init__(self, value: Value):
        self.value = value

    def __str__(self):
        return "WRITE {}".format(self.value)

    def __repr__(self):
        return str(self)
