from model.nonterminals.Condition import Condition


class If:

    def __init__(self, condition: Condition, commands: list, lineno: int = None):
        self.lineno = lineno
        self.condition = condition
        self.commands = commands

    def __str__(self):
        return "IF {} THEN <commands>".format(self.condition)

    def __repr__(self):
        return str(self)

    def get_changed_identifiers(self):
        changed_identifiers = []
        for c in self.commands:
            changed_identifiers += c.get_changed_identifiers()
        return changed_identifiers
