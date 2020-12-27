class DeclareArray:

    def __init__(self, name: str, first: int, last: int):
        self.name = name
        self.first = first
        self.last = last

    def __str__(self):
        return "DECLARE {}({}, {})".format(self.name, self.first, self.last)

    def __repr__(self):
        return str(self)
