from model.nonterminals.Value import Value


class ForDownto:

    def __init__(self, idd: str, from_value: Value, downto_value: Value, commands: list):
        self.idd = idd
        self.from_value = from_value
        self.downto_value = downto_value
        self.commands = commands

    def __str__(self):
        return "FOR {} FROM {} DOWNTO {} DO <commands>".format(self.idd, self.from_value, self.downto_value)

    def __repr__(self):
        return str(self)
