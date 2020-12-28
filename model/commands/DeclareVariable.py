class DeclareVariable:

    def __init__(self, name: str, lineno: int = None):
        self.lineno = lineno
        self.name = name

    def __str__(self):
        return "DECLARE {}".format(self.name)

    def __repr__(self):
        return str(self)
