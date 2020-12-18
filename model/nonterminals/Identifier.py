class Identifier:

    def __init__(self, name: str, offset=None):
        self.name = name
        self.offset = offset

    def __str__(self):
        if not self.offset:
            return self.name
        else:
            return "{}({})".format(self.name, str(self.offset))

    def __repr__(self):
        return str(self)
