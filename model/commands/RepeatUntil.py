from model.nonterminals.Condition import Condition


class RepeatUntil:

    def __init__(self, commands: list, condition: Condition, lineno: int = None):
        self.lineno = lineno
        self.commands = commands
        self.condition = condition

    def __str__(self):
        return "REPEAT <commands> UNTIL {}".format(self.condition)

    def __repr__(self):
        return str(self)

    def get_changed_identifiers(self):
        changed_identifiers = []
        for c in self.commands:
            changed_identifiers += c.get_changed_identifiers()
        return changed_identifiers
