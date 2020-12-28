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
