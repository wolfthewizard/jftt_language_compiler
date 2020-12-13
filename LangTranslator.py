from LangVariableTable import LangVariableTable
from Model import ReferenceObject


class LangTranslator:

    def __init__(self):
        self.variable_table = LangVariableTable()

    @staticmethod
    def __generate_constant(value, register="a"):
        commands = []
        while value:
            if value % 2:
                commands.append("INC " + register)
                value -= 1
            else:
                commands.append("SHL " + register)
                value //= 2
        commands.append("RESET " + register)
        return "\n".join(commands[::-1])

    def __generate_address(self, ref_obj, register="a", initialize=False):
        if not initialize:
            address = self.variable_table.get_address(ref_obj.name, ref_obj.offset)
        else:
            address = self.variable_table.init_and_get_address(ref_obj.name, ref_obj.offset)
        return self.__generate_constant(address, register)

    def __generate(self, parameter, register="a", initialize=False):
        if type(parameter) == int:
            return self.__generate_constant(parameter, register)
        else:
            return self.__generate_address(parameter, register, initialize)

    def declare_variable(self, name):
        self.variable_table.add_variable(name)

    def declare_array(self, name, first, last):
        self.variable_table.add_array(name, first, last)

    def assign_value(self, ref_obj, value):
        code = ""
        code += self.__generate(value) + "\n"
        code += self.__generate(ref_obj, "b", initialize=True) + "\n"
        code += "STORE a b"
        return code

    def read(self, ref_obj):
        code = ""
        code += self.__generate(ref_obj, initialize=True) + "\n"
        code += "GET a"
        return code

    def write(self, par):
        code = ""
        code += self.__generate(par) + "\n"
        code += "PUT a"
        return code

    def add(self, a):
        pass
