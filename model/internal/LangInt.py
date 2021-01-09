from model.errors import *


class LangInt:

    def __init__(self, adr):
        self.__address = adr
        self.__initialized = False
        self.__value = None

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
            raise InvalidReferenceError
        return self.__value

    def set_value(self, value, offset=None):
        if offset is not None:
            raise InvalidReferenceError
        self.__value = value
