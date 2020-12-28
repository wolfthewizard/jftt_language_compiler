class Stack:

    def __init__(self):
        self.contents = dict()

    def __contains__(self, item):
        return item in self.contents.keys()

    def insert(self, key, element):
        if key in self.contents.keys():
            self.contents[key].append(element)
        else:
            self.contents[key] = [element]

    def get(self, key):
        if key in self.contents.keys():
            element = self.contents[key][-1]
            return element
        else:
            raise KeyError

    def pop(self, key):
        if key in self.contents.keys():
            element = self.contents[key].pop()
            if not len(self.contents[key]):
                del self.contents[key]
            return element
        else:
            raise KeyError
