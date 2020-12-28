from model.nonterminals.Condition import Condition


class IfElse:

    def __init__(self, condition: Condition, positive_commands: list, negative_commands: list, lineno: int = None):
        self.lineno = lineno
        self.condition = condition
        self.positive_commands = positive_commands
        self.negative_commands = negative_commands

    def __str__(self):
        return "IF {} THEN <commands> ELSE <commands>".format(self.condition)

    def __repr__(self):
        return str(self)
