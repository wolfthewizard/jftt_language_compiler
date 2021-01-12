from model.errors import *
from model.internal.LangInt import LangInt
from model.internal.LangArray import LangArray
from model.internal.Stack import Stack
from copy import deepcopy


class LangVariableTable:

    def __init__(self):
        self.__stack = Stack()
        self.__table = dict()
        self.__marker = 0

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
        name = str(self.__marker)
        var = LangInt(self.__marker)
        var.initialize()
        self.__marker += 1
        self.__table[name] = var
        return name

    def remove_variable(self, name):
        self.__marker -= 1
        del self.__table[name]

    def get_address(self, name, offset=None, initialize=False):
        try:
            if name in self.__stack:
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

    def get_marker(self):
        return self.__marker

    def get_value(self, name, offset=None):
        if name in self.__stack:
            return None
        var = self.__table[name]
        if offset is not None and type(offset) != int:
            offset = self.get_value(offset)
        return var.get_value(offset)

    def set_value(self, value, name, offset=None):
        if name in self.__stack:
            pass
        else:
            var = self.__table[name]
            if offset is not None and type(offset) != int:
                offset = self.get_value(offset)
            var.set_value(value, offset)

    def clone(self):
        var_table = LangVariableTable()
        var_table.__stack = self.__stack.clone()
        var_table.__table = deepcopy(self.__table)
        var_table.__marker = self.__marker
        return var_table

    def merge_from_one(self, other):
        for name in self.__table.keys():
            self.__table[name] = self.__table[name].merge(other.__table[name])

    def merge_from_two(self, other1, other2):
        for name in self.__table.keys():
            self.__table[name] = other1.__table[name].merge(other2.__table[name])

    def unset_from_list(self, identifier_list):
        for idd in identifier_list:
            try:
                self.set_value(None, idd.name, idd.offset)
            except KeyError:
                self.set_value(None, idd.name, None)
