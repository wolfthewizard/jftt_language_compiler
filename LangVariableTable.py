from errors import *
from LangInt import LangInt
from LangArray import LangArray


class LangVariableTable:

    def __init__(self):
        self.__table = dict()
        self.__marker = 0

    def add_variable(self, name):
        if name in self.__table:
            raise SecondDeclarationError
        self.__table[name] = LangInt()

    def add_array(self, name, first, last):
        if name in self.__table:
            raise SecondDeclarationError
        arr = LangArray(first, last)
        self.__table[name] = arr
        arr.address = self.__marker
        self.__marker += len(arr)

    def get_address(self, name, offset=None):
        try:
            return self.__table[name].get_address(offset)
        except (VariableUnitilializedError, InvalidReferenceError) as e:
            raise e
        except KeyError:
            raise VariableUndeclaredError

    def init_and_get_address(self, name, offset=None):
        try:
            var = self.__table[name]
            if not var.is_initialized():
                var.set_address(self.__marker)
                self.__marker += 1
            return self.get_address(name, offset)
        except (VariableUnitilializedError, InvalidReferenceError) as e:
            raise e
        except KeyError:
            raise VariableUndeclaredError
