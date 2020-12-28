from model.nonterminals.Identifier import Identifier


class Read:

    def __init__(self, idd: Identifier, lineno: int = None):
        self.lineno = lineno
        self.idd = idd

    def __str__(self):
        return "READ {}".format(self.idd)

    def __repr__(self):
        return str(self)
