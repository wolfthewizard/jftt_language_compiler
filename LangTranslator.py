from LangVariableTable import LangVariableTable


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
        address = self.variable_table.get_address(ref_obj.name, ref_obj.offset, initialize)
        code = self.__generate_constant(address, register)
        if ref_obj.offset is None or type(ref_obj.offset) == int:
            return code
        else:
            bias = self.variable_table.get_bias(ref_obj.name)
            reg = "b" if register == "a" else "c"
            offset_address = self.variable_table.get_address(ref_obj.offset, None)
            code += self.__generate_constant() + "\n"
            code += "LOAD " + reg + " " + reg
            return code
            # todo: finish this code after splitting functions into more atomic methods
            #       establish new convention where methods have name of matched non-terminal to hint their purpose

    def __generate(self, parameter, register="a", initialize=False):
        if type(parameter) == int:
            return self.__generate_constant(parameter, register)
        else:
            return self.__generate_address(parameter, register, initialize)

    def declare_variable(self, name):
        self.variable_table.add_variable(name)

    def declare_array(self, name, first, last):
        self.variable_table.add_array(name, first, last)

    def assign_value(self, ref_target, ref_source):
        code = ""
        if type(ref_source) == int:
            code += self.__generate_constant(ref_source) + "\n"
        else:
            code += self.__generate_address(ref_source) + "\n"
            code += "LOAD a a\n"
        code += self.__generate(ref_target, "b", initialize=True) + "\n"
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
