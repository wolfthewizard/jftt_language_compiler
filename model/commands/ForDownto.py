from model.nonterminals.Value import Value


class ForDownto:

    def __init__(self, idd: str, from_value: Value, downto_value: Value, commands: list, lineno: int = None):
        self.lineno = lineno
        self.idd = idd
        self.from_value = from_value
        self.downto_value = downto_value
        self.commands = commands

    def __str__(self):
        return "FOR {} FROM {} DOWNTO {} DO <commands>".format(self.idd, self.from_value, self.downto_value)

    def __repr__(self):
        return str(self)

    def get_changed_identifiers(self):
        changed_identifiers = []
        for c in self.commands:
            changed_identifiers += c.get_changed_identifiers()
        return changed_identifiers
