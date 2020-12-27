from model.nonterminals.Condition import Condition


class If:

    def __init__(self, condition: Condition, commands: list):
        self.condition = condition
        self.commands = commands

    def __str__(self):
        return "IF {} THEN <commands>".format(self.condition)

    def __repr__(self):
        return str(self)
