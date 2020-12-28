from model.nonterminals.Value import Value


class Write:

    def __init__(self, value: Value, lineno: int = None):
        self.lineno = lineno
        self.value = value

    def __str__(self):
        return "WRITE {}".format(self.value)

    def __repr__(self):
        return str(self)
