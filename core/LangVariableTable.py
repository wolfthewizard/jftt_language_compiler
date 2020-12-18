from model.errors import *
from model.internal.LangInt import LangInt
from model.internal.LangArray import LangArray


class LangVariableTable:

    def __init__(self):
        self.__table = dict()
        self.__marker = 1

    def add_variable(self, name):
        if name in self.__table:
            raise SecondDeclarationError
        self.__table[name] = LangInt(self.__marker)
        self.__marker += 1

    def add_array(self, name, first, last):
        if name in self.__table:
            raise SecondDeclarationError
        arr = LangArray(first, last, self.__marker)
        self.__table[name] = arr
        self.__marker += len(arr)

    def get_address(self, name, offset=None, initialize=False):
        try:
            var = self.__table[name]
            if initialize:
                var.initialize()
            return var.get_address(offset)
        except (VariableUnitilializedError, InvalidReferenceError) as e:
            raise e
        except KeyError:
            raise VariableUndeclaredError

    def get_bias(self, name):
        return self.__table[name].get_bias()
