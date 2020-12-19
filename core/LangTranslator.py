from core.LangVariableTable import LangVariableTable
from core.LangRegisterMachine import LangRegisterMachine
from model.nonterminals.Expression import Expression
from model.nonterminals.Value import Value
from model.nonterminals.Identifier import Identifier
from model.nonterminals.Condition import Condition


class LangTranslator:

    def __init__(self):
        self.variable_table = LangVariableTable()
        self.register_machine = LangRegisterMachine()

    def __put_value_to_register(self, val: Value, register, initialize=False) -> str:
        if val.is_int():
            return self.__generate_constant(val.core, register)
        else:
            code = self.__put_address_to_register(val.core, register, initialize)
            code += "\nLOAD {} {}".format(register, register)
            return code

    def __put_address_to_register(self, idd: Identifier, register, initialize=False) -> str:
        if idd.offset is None or type(idd.offset) == int:
            address = self.variable_table.get_address(idd.name, idd.offset, initialize)
            code = self.__generate_constant(address, register)
            return code
        else:
            bias = self.variable_table.get_bias(idd.name)
            address = self.variable_table.get_address(idd.name, bias, initialize)
            reg = self.register_machine.borrow_register()

            code = self.__generate_constant(address, register)
            code += "\n" + self.__put_value_to_register(Value(Identifier(idd.offset)), register=reg)
            code += "\nADD {} {}".format(register, reg)
            code += "\n" + self.__put_value_to_register(Value(bias), register=reg)
            code += "\nSUB {} {}".format(register, reg)
            return code

    @staticmethod
    def __copy_register(source_reg: str, dest_reg: str):
        return "RESET {}\nADD {} {}".format(dest_reg, dest_reg, source_reg)

    @staticmethod
    def __generate_constant(value: int, register) -> str:
        commands = []
        while value:
            if value % 2:
                commands.append("INC {}".format(register))
                value -= 1
            else:
                commands.append("SHL {}".format(register))
                value //= 2
        commands.append("RESET {}".format(register))
        return "\n".join(commands[::-1])

    def __perform_operation(self, reg1: str, reg2: str, operation: str):
        if operation == "+":
            return self.__perform_addition(reg1, reg2)
        elif operation == "-":
            return self.__perform_subtraction(reg1, reg2)
        elif operation == "*":
            return self.__perform_multiplication(reg1, reg2)
        elif operation == "/":
            return self.__perform_division(reg1, reg2)
        else:
            return self.__perform_modulo(reg1, reg2)

    @staticmethod
    def __perform_addition(reg1: str, reg2: str):
        code = "ADD {} {}".format(reg1, reg2)
        return code

    @staticmethod
    def __perform_subtraction(reg1: str, reg2: str):
        code = "SUB {} {}".format(reg1, reg2)
        return code

    def __perform_multiplication(self, reg1: str, reg2: str):
        helper_reg = self.register_machine.borrow_register()

        code = self.__copy_register(source_reg=reg1, dest_reg=helper_reg)
        code += "\nRESET {}".format(reg1)
        code += "\nJZERO {} 8".format(reg2)
        code += "\nJODD {} 4".format(reg2)
        code += "\nSHR {}".format(reg2)
        code += "\nSHL {}".format(helper_reg)
        code += "\nJUMP -4"
        code += "\nADD {} {}".format(reg1, helper_reg)
        code += "\nDEC {}".format(reg2)
        code += "\nJUMP -7"
        return code

    def __perform_division(self, reg1: str, reg2: str):
        pass

    def __perform_modulo(self, reg1: str, reg2: str):
        pass

    def declare_variable(self, name):
        self.variable_table.add_variable(name)

    def declare_array(self, name, first, last):
        self.variable_table.add_array(name, first, last)

    def assign(self, changed_identifier: Identifier, assigned_expression: Expression) -> str:
        if assigned_expression.is_value():
            return self.__assign_value(changed_identifier, assigned_expression.val1)
        else:
            return self.__assign_expression(changed_identifier, assigned_expression)

    def __assign_value(self, changed_identifier: Identifier, assigned_value: Value) -> str:
        value_reg = self.register_machine.fetch_register()
        address_reg = self.register_machine.fetch_register()

        code = self.__put_value_to_register(assigned_value, register=value_reg)
        code += "\n" + self.__put_address_to_register(changed_identifier, register=address_reg, initialize=True)
        code += "\nSTORE {} {}".format(value_reg, address_reg)
        return code

    def __assign_expression(self, changed_identifier: Identifier, assigned_expression: Expression) -> str:
        address_reg = self.register_machine.fetch_register()
        val1_reg = self.register_machine.fetch_register()
        val2_reg = self.register_machine.fetch_register()

        code = self.__put_address_to_register(changed_identifier, register=address_reg, initialize=True)
        code += "\n" + self.__put_value_to_register(assigned_expression.val1, register=val1_reg)
        code += "\n" + self.__put_value_to_register(assigned_expression.val2, register=val2_reg)
        code += "\n" + self.__perform_operation(val1_reg, val2_reg, operation=assigned_expression.operation)
        code += "\nSTORE {} {}".format(val1_reg, address_reg)
        return code

    def read(self, idd: Identifier) -> str:
        reg = self.register_machine.fetch_register()
        code = self.__put_address_to_register(idd, register=reg, initialize=True)
        code += "\nGET {}".format(reg)
        return code

    def write(self, val: Value) -> str:
        reg = self.register_machine.fetch_register()
        if val.is_int():
            reg2 = self.register_machine.fetch_register()
            code = self.__put_value_to_register(val, register=reg)
            code += "\nRESET {}".format(reg2)
            code += "\nSTORE {} {}".format(reg, reg2)
            code += "\nPUT {}".format(reg2)
        else:
            code = self.__put_address_to_register(val.core, register=reg)
            code += "\nPUT {}".format(reg)
        return code
