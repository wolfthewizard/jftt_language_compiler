class Value:

    def __init__(self, core):
        self.core = core

    def __str__(self):
        return str(self.core)

    def __repr__(self):
        return str(self.core)

    def is_int(self):
        return type(self.core) == int
