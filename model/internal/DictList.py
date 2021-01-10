class DictList:

    def __init__(self):
        self.__items = dict()

    def __getitem__(self, item):
        try:
            return self.__items[item]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        if value is None and key in self.__items.keys():
            del self.__items[key]
        else:
            self.__items[key] = value

    def reset(self):
        del self.__items
        self.__items = dict()

    def keys(self):
        for k in self.__items.keys():
            yield k
