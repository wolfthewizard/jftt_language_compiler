from core.LangVariableTable import LangVariableTable
from model.nonterminals.Expression import Expression
from model.nonterminals.Value import Value
from model.nonterminals.Identifier import Identifier
from model.nonterminals.Condition import Condition


class LangTranslator:

    def __init__(self):
        self.variable_table = LangVariableTable()

    @staticmethod
    def __generate_constant(value: int, register="a"):
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

    def __generate_address(self, identifier: Identifier, register="a", initialize=False):
        address = self.variable_table.get_address(identifier.name, identifier.offset, initialize)
        code = self.__generate_constant(address, register)
        if identifier.offset is None or type(identifier.offset) == int:
            return code
        else:
            bias = self.variable_table.get_bias(identifier.name)
            reg = "b" if register == "a" else "c"
            offset_address = self.variable_table.get_address(identifier.offset, None)
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

    def assign(self, changed_identifier: Identifier, assigned_expression: Expression) -> str:
        if assigned_expression.is_value():
            return self.__assign_value(changed_identifier, assigned_expression.val1)
        else:
            pass    # todo: implement handling operations (will probably split method)

    def __assign_value(self, changed_identifier: Identifier, assigned_value: Value) -> str:
        code = ""
        if assigned_value.is_int():
            code += self.__generate_constant(assigned_value.core) + "\n"
        else:
            code += self.__generate_address(assigned_value.core) + "\n"
            code += "LOAD a a\n"
        code += self.__generate(changed_identifier, "b", initialize=True) + "\n"
        code += "STORE a b"
        return code

    def read(self, id: Identifier):
        code = ""
        code += self.__generate(id, initialize=True) + "\n"
        code += "GET a"
        return code

    def write(self, val: Value):
        code = ""
        code += self.__generate(val.core) + "\n"
        code += "PUT a"
        return code
