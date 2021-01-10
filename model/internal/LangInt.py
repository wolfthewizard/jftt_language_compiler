from model.errors import *


class LangInt:

    def __init__(self, adr):
        self.__address = adr
        self.__initialized = False
        self.__value = None

    def __str__(self):
        val_str = str(self.__value) if self.__value is not None else "?"
        return val_str

    def __repr__(self):
        return str(self)

    def get_address(self, offset=None):
        if offset is not None:
            raise InvalidReferenceError
        elif not self.__initialized:
            raise VariableUnitilializedError
        else:
            return self.__address

    def set_address(self, adr):
        if self.__address is not None:
            raise SecondInitializationError
        self.__address = adr

    def is_initialized(self):
        return self.__initialized

    def initialize(self):
        self.__initialized = True

    def get_value(self, offset=None):
        if offset is not None:
            return None     # it's an exception, but it will be handled later
        return self.__value

    def set_value(self, value, offset=None):
        if offset is not None:
            return None     # it's an exception, but it will be handled later
        self.__value = value

    def merge(self, other):
        new = LangInt(self.__address)
        new.__initialized = self.__initialized
        new.__value = self.__value if self.__value == other.__value else None
        return new
