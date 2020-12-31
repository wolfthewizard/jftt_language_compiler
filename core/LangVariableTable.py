from model.errors import *
from model.internal.LangInt import LangInt
from model.internal.LangArray import LangArray
from model.internal.Stack import Stack
import random


class LangVariableTable:

    alphabet = "qwertyuiopasdfghjklzxcvbnm"

    def __init__(self):
        self.__stack = Stack()
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

    def add_iterator(self, name):
        iterator = LangInt(self.__marker)
        iterator.initialize()
        self.__marker += 1
        self.__stack.insert(name, iterator)

    def remove_iterator(self, name):
        self.__stack.pop(name)
        self.__marker -= 1

    def fetch_random_variable(self):
        name = random.choice(LangVariableTable.alphabet)
        while name in self.__table.keys() or name in self.__stack:
            name += random.choice(LangVariableTable.alphabet)
        var = LangInt(self.__marker)
        self.__marker += 1
        self.__table[name] = var
        return name

    def remove_variable(self, name):
        self.__marker -= 1
        del self.__table[name]

    def get_address(self, name, offset=None, initialize=False, ignore_iterator=None):
        try:
            if name in self.__stack and name != ignore_iterator:
                var = self.__stack.get(name)
                if initialize:
                    raise IteratorAssignmentError
            else:
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
