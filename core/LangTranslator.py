from core.LangVariableTable import LangVariableTable
from core.LangRegisterMachine import LangRegisterMachine
from model.internal.LangProgram import LangProgram
from model.internal.Feedback import Feedback
from model.nonterminals.Expression import Expression
from model.nonterminals.Value import Value
from model.nonterminals.Identifier import Identifier
from model.nonterminals.Condition import Condition
from model.commands.Assign import Assign
from model.commands.DeclareVariable import DeclareVariable
from model.commands.DeclareArray import DeclareArray
from model.commands.ForDownto import ForDownto
from model.commands.ForTo import ForTo
from model.commands.If import If
from model.commands.IfElse import IfElse
from model.commands.Read import Read
from model.commands.RepeatUntil import RepeatUntil
from model.commands.While import While
from model.commands.Write import Write
from model.errors import *


def is_power_of_two(num: int) -> bool:
    if num == 0:
        return False

    while num > 1:
        if num % 2:
            return False
        num //= 2
    return True


def log(num: int) -> int:
    res = 0
    while num > 1:
        res += 1
        num //= 2
    return res


class LangTranslator:

    ADDITION_SWITCH_THRESHOLD = 10
    MULTIPLICATION_SWITCH_THRESHOLD = 1_000_000

    def __init__(self):
        self.variable_table = LangVariableTable()
        self.register_machine = LangRegisterMachine()

    def translate_program(self, program: LangProgram):
        for declaration in program.declarations:
            self.declare(declaration)
        code = self.generate_code(program.commands)
        code += "\nHALT"
        return code

    def declare(self, declaration):
        try:
            if type(declaration) == DeclareVariable:
                self.declare_variable(declaration.name)
            else:
                self.declare_array(declaration.name, declaration.first, declaration.last)
        except CodeException as e:
            raise type(e)(e.args[0].format(declaration.lineno))

    def generate_code(self, commands: list) -> str:
        command_codes = []
        for command in commands:
            command_codes.append(self.unwrap_command(command))
        code = "\n".join(command_codes)
        return code

    def unwrap_command(self, command) -> str:
        try:
            if type(command) == Assign:
                return self.assign(command.changed_identifier, command.assigned_expression)
            elif type(command) == If:
                return self.if_then(command.condition, command.commands)
            elif type(command) == IfElse:
                return self.if_then_else(command.condition, command.positive_commands, command.negative_commands)
            elif type(command) == While:
                return self.while_do(command.condition, command.commands)
            elif type(command) == RepeatUntil:
                return self.repeat_until(command.commands, command.condition)
            elif type(command) == ForTo:
                return self.for_to(command.idd, command.from_value, command.to_value, command.commands)
            elif type(command) == ForDownto:
                return self.for_downto(command.idd, command.from_value, command.downto_value, command.commands)
            elif type(command) == Read:
                return self.read(command.idd)
            else:
                return self.write(command.value)
        except CodeException as e:
            raise type(e)(e.args[0].format(command.lineno))

    @staticmethod
    def __line_count(text: str) -> int:
        return text.count("\n") + 1

    def __put_value_to_register(self, val: Value, register, initialize=False, ignore_iterator=None) -> str:
        if val.is_int():
            return self.__generate_constant(val.core, register)
        else:
            code = self.__put_address_to_register(val.core, register, initialize, ignore_iterator)
            code += "\nLOAD {} {}".format(register, register)
            return code

    def __put_address_to_register(self, idd: Identifier, register, initialize=False, ignore_iterator=None) -> str:
        if idd.offset is None or type(idd.offset) == int:
            address = self.variable_table.get_address(idd.name, idd.offset, initialize, ignore_iterator)
            code = self.__generate_constant(address, register)
            return code
        else:
            bias = self.variable_table.get_bias(idd.name)
            address = self.variable_table.get_address(idd.name, bias, initialize, ignore_iterator)
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

    def __perform_operation(self, left_val: Value, right_val: Value, operation: str) -> Feedback:
        if operation == "+":
            return self.__perform_addition(left_val, right_val)
        elif operation == "-":
            return self.__perform_subtraction(left_val, right_val)
        elif operation == "*":
            return self.__perform_multiplication(left_val, right_val)
        elif operation == "/":
            return self.__perform_division(left_val, right_val)
        else:
            return self.__perform_modulo(left_val, right_val)

    def __perform_addition(self, left_val: Value, right_val: Value) -> Feedback:
        if left_val.is_int() and right_val.is_int():
            reg = self.register_machine.fetch_register()
            code = self.__generate_constant(left_val.core + right_val.core, reg)
            return Feedback(code, reg)
        elif left_val.is_int() or right_val.is_int():
            if left_val.is_int():
                num = left_val.core
                val = right_val
            else:
                num = right_val.core
                val = left_val
            if num > LangTranslator.ADDITION_SWITCH_THRESHOLD:
                return self.__perform_addition_2i(left_val, right_val)
            reg = self.register_machine.fetch_register()
            code = self.__put_value_to_register(val, reg)
            code += "\n" + "\n".join(["INC {}".format(reg) for _ in range(num)])
            return Feedback(code, reg)
        else:
            if left_val == right_val:
                reg = self.register_machine.fetch_register()
                code = self.__put_value_to_register(left_val, reg)
                code += "\nSHL {}".format(reg)
                return Feedback(code, reg)
            else:
                return self.__perform_addition_2i(left_val, right_val)

    def __perform_addition_2i(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()

        code = self.__put_value_to_register(left_val, reg1)
        code += "\n" + self.__put_value_to_register(right_val, reg2)
        code += "\nADD {} {}".format(reg1, reg2)
        return Feedback(code, reg1)

    def __perform_subtraction(self, left_val: Value, right_val: Value) -> Feedback:
        if left_val.is_int() and right_val.is_int():
            reg = self.register_machine.fetch_register()
            num = abs(left_val.core - right_val.core)
            code = self.__generate_constant(num, reg)
            return Feedback(code, reg)
        elif right_val.is_int():
            num = right_val.core
            if num > LangTranslator.ADDITION_SWITCH_THRESHOLD:
                return self.__perform_subtraction_2i(left_val, right_val)
            reg = self.register_machine.fetch_register()
            code = self.__put_value_to_register(left_val, reg)
            code += "\n" + "\n".join(["DEC {}".format(reg) for _ in range(num)])
            return Feedback(code, reg)
        else:
            if not left_val.is_int() and left_val == right_val:
                reg = self.register_machine.fetch_register()
                code = "RESET {}".format(reg)
                return Feedback(code, reg)
            else:
                return self.__perform_subtraction_2i(left_val, right_val)

    def __perform_subtraction_2i(self, left_val: Value, right_val: Value) -> Feedback:
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()

        code = self.__put_value_to_register(left_val, reg1)
        code += "\n" + self.__put_value_to_register(right_val, reg2)
        code += "\nSUB {} {}".format(reg1, reg2)
        return Feedback(code, reg1)

    def __perform_multiplication(self, left_val: Value, right_val: Value) -> Feedback:
        if left_val.is_int() and right_val.is_int():
            reg = self.register_machine.fetch_register()
            code = self.__generate_constant(left_val.core * right_val.core, reg)
            return Feedback(code, reg)
        elif left_val.is_int() or right_val.is_int():
            if left_val.is_int():
                num = left_val.core
                val = right_val
            else:
                num = right_val.core
                val = left_val
            if num == 0:
                reg = self.register_machine.fetch_register()
                code = "RESET {}".format(reg)
                return Feedback(code, reg)
            elif num < LangTranslator.MULTIPLICATION_SWITCH_THRESHOLD and is_power_of_two(num):
                reg = self.register_machine.fetch_register()
                code = self.__put_value_to_register(val, reg)
                code += "\n" + "\n".join(["SHL {}".format(reg) for _ in range(log(num))])
                return Feedback(code, reg)
            else:
                return self.__perform_multiplication_2i(left_val, right_val)
        else:
            return self.__perform_multiplication_2i(left_val, right_val)

    def __perform_multiplication_2i(self, left_val: Value, right_val: Value) -> Feedback:
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        helper_reg = self.register_machine.borrow_register()

        code = self.__put_value_to_register(left_val, reg1)
        code += "\n" + self.__put_value_to_register(right_val, reg2)
        code += "\n" + self.__copy_register(source_reg=reg2, dest_reg=helper_reg)
        code += "\nSUB {} {}".format(helper_reg, reg1)
        code += "\nJZERO {} 7".format(helper_reg)
        code += "\n" + self.__copy_register(source_reg=reg2, dest_reg=helper_reg)
        code += "\n" + self.__copy_register(source_reg=reg1, dest_reg=reg2)
        code += "\nRESET {}".format(reg1)
        code += "\nJUMP 6"
        code += "\nADD {} {}".format(helper_reg, reg1)
        code += "\nRESET {}".format(reg1)
        code += "\nJUMP 3"
        code += "\nADD {} {}".format(reg1, helper_reg)
        code += "\nDEC {}".format(reg2)
        code += "\nJZERO {} 5".format(reg2)
        code += "\nJODD {} -3".format(reg2)
        code += "\nSHR {}".format(reg2)
        code += "\nSHL {}".format(helper_reg)
        code += "\nJUMP -4"
        return Feedback(code, reg1)

    def __perform_division(self, left_val: Value, right_val: Value) -> Feedback:
        if left_val.is_int() and right_val.is_int():
            reg = self.register_machine.fetch_register()
            if right_val.core == 0:
                code = "RESET {}".format(reg)
            else:
                code = self.__generate_constant(left_val.core // right_val.core, reg)
            return Feedback(code, reg)
        elif right_val.is_int():
            num = right_val.core
            if num == 0:
                reg = self.register_machine.fetch_register()
                code = "RESET {}".format(reg)
                return Feedback(code, reg)
            elif num < LangTranslator.MULTIPLICATION_SWITCH_THRESHOLD and is_power_of_two(num):
                reg = self.register_machine.fetch_register()
                code = self.__put_value_to_register(left_val, reg)
                code += "\n" + "\n".join(["SHR {}".format(reg) for _ in range(log(num))])
                return Feedback(code, reg)
            else:
                return self.__perform_division_2i(left_val, right_val)
        else:
            if not left_val.is_int() and left_val == right_val:
                reg = self.register_machine.fetch_register()
                helper_reg = self.register_machine.fetch_register()
                code = self.__put_value_to_register(left_val, helper_reg)
                code += "\nRESET {}".format(reg)
                code += "\nJZERO {} 2".format(helper_reg)
                code += "\nINC {}".format(reg)
                return Feedback(code, reg)
            else:
                return self.__perform_division_2i(left_val, right_val)

    def __perform_division_2i(self, left_val: Value, right_val: Value) -> Feedback:
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        check_reg, mult_reg, dividend_reg = self.register_machine.borrow_registers(3)

        code = self.__put_value_to_register(right_val, reg2)
        code += "\nRESET {}".format(reg1)
        code += "\nJZERO {}".format(reg2)                       # END
        snippet = self.__put_value_to_register(left_val, dividend_reg)
        code += " {}".format(31 + self.__line_count(snippet))
        code += "\n" + snippet
        code += "\nRESET {}".format(mult_reg)
        code += "\nINC {}".format(mult_reg)
        code += "\n" + self.__copy_register(reg2, check_reg)
        code += "\nSUB {} {}".format(check_reg, dividend_reg)
        code += "\nJZERO {} 2".format(check_reg)
        code += "\nJUMP 24"                                     # END
        code += "\nINC {}".format(reg1)
        # beginning of 1st loop
        code += "\nSHL {}".format(mult_reg)
        code += "\nSHL {}".format(reg2)
        code += "\nSHL {}".format(reg1)
        code += "\nADD {} {}".format(check_reg, reg2)
        code += "\nSUB {} {}".format(check_reg, dividend_reg)
        code += "\nJZERO {} -5".format(check_reg)
        # end of the loop
        code += "\nSHR {}".format(reg2)
        code += "\nSHR {}".format(mult_reg)
        code += "\nSHR {}".format(reg1)
        code += "\nSUB {} {}".format(dividend_reg, reg2)
        code += "\nRESET {}".format(check_reg)
        code += "\nJUMP 3"
        # beginning of 2nd loop
        code += "\nADD {} {}".format(reg1, mult_reg)
        code += "\nSUB {} {}".format(dividend_reg, reg2)
        code += "\nSHR {}".format(mult_reg)
        code += "\nJZERO {} 7".format(mult_reg)                 # END
        code += "\nSHR {}".format(reg2)
        code += "\nADD {} {}".format(check_reg, reg2)
        code += "\nSUB {} {}".format(check_reg, dividend_reg)
        code += "\nJZERO {} -7".format(check_reg)
        code += "\nRESET {}".format(check_reg)
        code += "\nJUMP -7"

        return Feedback(code, reg1)

    def __perform_modulo(self, left_val: Value, right_val: Value) -> Feedback:
        if left_val.is_int() and right_val.is_int():
            reg = self.register_machine.fetch_register()
            if right_val.core == 0:
                code = "RESET {}".format(reg)
            else:
                code = self.__generate_constant(left_val.core % right_val.core, reg)
            return Feedback(code, reg)
        elif right_val.is_int():
            num = right_val.core
            if num == 0 or num == 1:
                reg = self.register_machine.fetch_register()
                code = "RESET {}".format(reg)
                return Feedback(code, reg)
            elif num == 2:
                reg = self.register_machine.fetch_register()
                code = self.__put_value_to_register(left_val, reg)
                code += "\nJODD {} 3".format(reg)
                code += "\nRESET {}".format(reg)
                code += "\nJUMP 3"
                code += "\nRESET {}".format(reg)
                code += "\nINC {}".format(reg)
                return Feedback(code, reg)
            else:
                return self.__perform_modulo_2i(left_val, right_val)
        else:
            if not left_val.is_int() and left_val == right_val:
                reg = self.register_machine.fetch_register()
                code = "RESET {}".format(reg)
                return Feedback(code, reg)
            else:
                return self.__perform_modulo_2i(left_val, right_val)

    def __perform_modulo_2i(self, left_val: Value, right_val: Value) -> Feedback:
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        check_reg, mult_reg, division_result_reg = self.register_machine.borrow_registers(3)

        code = self.__put_value_to_register(right_val, reg2)
        code += "\nRESET {}".format(division_result_reg)
        code += "\nJZERO {}".format(reg2)  # END
        snippet = self.__put_value_to_register(left_val, reg1)
        code += " {}".format(31 + self.__line_count(snippet))
        code += "\n" + snippet
        code += "\nRESET {}".format(mult_reg)
        code += "\nINC {}".format(mult_reg)
        code += "\n" + self.__copy_register(reg2, check_reg)
        code += "\nSUB {} {}".format(check_reg, reg1)
        code += "\nJZERO {} 2".format(check_reg)
        code += "\nJUMP 25"  # END
        code += "\nINC {}".format(division_result_reg)
        # beginning of 1st loop
        code += "\nSHL {}".format(mult_reg)
        code += "\nSHL {}".format(reg2)
        code += "\nSHL {}".format(division_result_reg)
        code += "\nADD {} {}".format(check_reg, reg2)
        code += "\nSUB {} {}".format(check_reg, reg1)
        code += "\nJZERO {} -5".format(check_reg)
        # end of the loop
        code += "\nSHR {}".format(reg2)
        code += "\nSHR {}".format(mult_reg)
        code += "\nSHR {}".format(division_result_reg)
        code += "\nSUB {} {}".format(reg1, reg2)
        code += "\nRESET {}".format(check_reg)
        code += "\nJUMP 3"
        # beginning of 2nd loop
        code += "\nADD {} {}".format(division_result_reg, mult_reg)
        code += "\nSUB {} {}".format(reg1, reg2)
        code += "\nSHR {}".format(mult_reg)
        code += "\nJZERO {} 8".format(mult_reg)  # END
        code += "\nSHR {}".format(reg2)
        code += "\nADD {} {}".format(check_reg, reg2)
        code += "\nSUB {} {}".format(check_reg, reg1)
        code += "\nJZERO {} -7".format(check_reg)
        code += "\nRESET {}".format(check_reg)
        code += "\nJUMP -7"
        code += "\nRESET {}".format(reg1)

        return Feedback(code, reg1)

    def __perform_comparison(self, reg1: str, reg2: str, comparison: str):
        if comparison == "=":
            return self.__perform_equality(reg1, reg2)
        elif comparison == "!=":
            return self.__perform_inequality(reg1, reg2)
        elif comparison == "<":
            return self.__perform_less(reg1, reg2)
        elif comparison == ">":
            return self.__perform_more(reg1, reg2)
        elif comparison == "<=":
            return self.__perform_less_equal(reg1, reg2)
        else:
            return self.__perform_more_equal(reg1, reg2)

    def __perform_equality(self, reg1: str, reg2: str):
        condition_reg = self.register_machine.borrow_register()
        code = self.__copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP 5"
        code += "\n" + self.__copy_register(reg2, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg1)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP {}"
        return code

    def __perform_inequality(self, reg1: str, reg2: str):
        condition_reg = self.register_machine.borrow_register()
        code = self.__copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP 7"
        code += "\n" + self.__copy_register(reg2, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg1)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP 2"
        code += "\nJUMP {}"
        return code

    def __perform_less(self, reg1: str, reg2: str):
        condition_reg = self.register_machine.borrow_register()
        code = self.__copy_register(reg2, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg1)
        code += "\nJZERO {}".format(condition_reg) + " {}"
        return code

    def __perform_more(self, reg1: str, reg2: str):
        condition_reg = self.register_machine.borrow_register()
        code = self.__copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {}".format(condition_reg) + " {}"
        return code

    def __perform_less_equal(self, reg1: str, reg2: str):
        condition_reg = self.register_machine.borrow_register()
        code = self.__copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP {}"
        return code

    def __perform_more_equal(self, reg1: str, reg2: str):
        condition_reg = self.register_machine.borrow_register()
        code = self.__copy_register(reg2, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg1)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP {}"
        return code

    def declare_variable(self, name):
        self.variable_table.add_variable(name)

    def declare_array(self, name, first, last):
        self.variable_table.add_array(name, first, last)

    def assign(self, changed_identifier: Identifier, assigned_expression: Expression) -> str:
        # try:
        if assigned_expression.is_value():
            return self.__assign_value(changed_identifier, assigned_expression.val1)
        else:
            return self.__assign_expression(changed_identifier, assigned_expression)
        # except CodeException as e:
        #     raise type(e)(e.args[0].format(lineno))

    def __assign_value(self, changed_identifier: Identifier, assigned_value: Value) -> str:
        value_reg = self.register_machine.fetch_register()
        address_reg = self.register_machine.fetch_register()

        code = self.__put_value_to_register(assigned_value, register=value_reg)
        code += "\n" + self.__put_address_to_register(changed_identifier, register=address_reg, initialize=True)
        code += "\nSTORE {} {}".format(value_reg, address_reg)
        return code

    def __assign_expression(self, changed_identifier: Identifier, assigned_expression: Expression) -> str:
        address_reg = self.register_machine.fetch_register()

        code = self.__put_address_to_register(changed_identifier, register=address_reg, initialize=True)
        feedback = self.__perform_operation(assigned_expression.val1, assigned_expression.val2,
                                            operation=assigned_expression.operation)
        code += "\n" + feedback.code
        code += "\nSTORE {} {}".format(feedback.register, address_reg)
        return code

    def if_then_else(self, condition: Condition, positive_commands: list, negative_commands: list) -> str:
        positive_commands_code = self.generate_code(positive_commands)
        negative_commands_code = self.generate_code(negative_commands)
        val1_reg = self.register_machine.fetch_register()
        val2_reg = self.register_machine.fetch_register()

        code = self.__put_value_to_register(condition.val1, register=val1_reg)
        code += "\n" + self.__put_value_to_register(condition.val2, register=val2_reg)
        code += "\n" + self.__perform_comparison(val1_reg, val2_reg, condition.comparison).format(
            self.__line_count(positive_commands_code) + 2)
        code += "\n" + positive_commands_code
        code += "\nJUMP {}".format(self.__line_count(negative_commands_code) + 1)
        code += "\n" + negative_commands_code
        return code

    def if_then(self, condition: Condition, commands: list) -> str:
        commands_code = self.generate_code(commands)
        val1_reg = self.register_machine.fetch_register()
        val2_reg = self.register_machine.fetch_register()

        code = self.__put_value_to_register(condition.val1, register=val1_reg)
        code += "\n" + self.__put_value_to_register(condition.val2, register=val2_reg)
        code += "\n" + self.__perform_comparison(val1_reg, val2_reg, condition.comparison).format(
            self.__line_count(commands_code) + 1)
        code += "\n" + commands_code
        return code

    def while_do(self, condition: Condition, commands: list) -> str:
        commands_code = self.generate_code(commands)        # code has to be generated before fetching registers
        val1_reg = self.register_machine.fetch_register()   # because condition check requires registers to be freshly
        val2_reg = self.register_machine.fetch_register()   # fetched; in other case borrowed register inside check
                                                            # may be one of assigned registers
        code = self.__put_value_to_register(condition.val1, register=val1_reg)
        code += "\n" + self.__put_value_to_register(condition.val2, register=val2_reg)
        code += "\n" + self.__perform_comparison(val1_reg, val2_reg, condition.comparison).format(
            self.__line_count(commands_code) + 2)
        code += "\n" + commands_code
        code += "\nJUMP {}".format(-self.__line_count(code))
        return code

    def repeat_until(self, commands: list, condition: Condition) -> str:
        commands_code = self.generate_code(commands)
        val1_reg = self.register_machine.fetch_register()
        val2_reg = self.register_machine.fetch_register()

        code = commands_code
        code += "\n" + self.__put_value_to_register(condition.val1, register=val1_reg)
        code += "\n" + self.__put_value_to_register(condition.val2, register=val2_reg)
        code += "\n" + self.__perform_comparison(val1_reg, val2_reg, condition.comparison).format(2)
        code += "\nJUMP 2"
        code += "\nJUMP {}".format(-self.__line_count(code))
        return code

    def for_to(self, idd: str, from_value: Value, to_value: Value, commands: list):
        self.variable_table.add_iterator(idd)
        counter = self.variable_table.fetch_random_variable()
        commands_code = self.generate_code(commands)
        iterator_reg = self.register_machine.fetch_register()
        counter_reg = self.register_machine.fetch_register()
        temp_reg = self.register_machine.fetch_register()

        pre_run_code = self.__put_value_to_register(from_value, iterator_reg, ignore_iterator=idd)
        pre_run_code += "\n" + self.__put_address_to_register(Identifier(idd), temp_reg)
        pre_run_code += "\nSTORE {} {}".format(iterator_reg, temp_reg)
        pre_run_code += "\n" + self.__put_value_to_register(to_value, counter_reg, ignore_iterator=idd)
        pre_run_code += "\nINC {}".format(counter_reg)
        pre_run_code += "\nSUB {} {}".format(counter_reg, iterator_reg)
        pre_run_code += "\n" + self.__put_address_to_register(Identifier(counter), temp_reg, initialize=True)

        code = "JZERO {}".format(counter_reg) + " {}"
        code += "\nSTORE {} {}".format(counter_reg, temp_reg)
        code += "\n" + commands_code
        code += "\n" + self.__generate_constant(self.variable_table.get_address(idd), temp_reg)
        code += "\nLOAD {} {}".format(iterator_reg, temp_reg)
        code += "\nINC {}".format(iterator_reg)
        code += "\nSTORE {} {}".format(iterator_reg, temp_reg)
        code += "\n" + self.__put_address_to_register(Identifier(counter), temp_reg)
        code += "\nLOAD {} {}".format(counter_reg, temp_reg)
        code += "\nDEC {}".format(counter_reg)
        code += "\nJUMP {}".format(-self.__line_count(code))
        code = code.format(self.__line_count(code))

        self.variable_table.remove_variable(counter)
        self.variable_table.remove_iterator(idd)
        return pre_run_code + "\n" + code

    def for_downto(self, idd: str, from_value: Value, downto_value: Value, commands: list):
        self.variable_table.add_iterator(idd)
        counter = self.variable_table.fetch_random_variable()
        commands_code = self.generate_code(commands)
        iterator_reg = self.register_machine.fetch_register()
        counter_reg = self.register_machine.fetch_register()
        temp_reg = self.register_machine.fetch_register()

        pre_run_code = self.__put_value_to_register(from_value, iterator_reg, ignore_iterator=idd)
        pre_run_code += "\n" + self.__put_address_to_register(Identifier(idd), temp_reg)
        pre_run_code += "\nSTORE {} {}".format(iterator_reg, temp_reg)
        pre_run_code += "\n" + self.__copy_register(iterator_reg, counter_reg)
        pre_run_code += "\nINC {}".format(counter_reg)
        pre_run_code += "\n" + self.__put_value_to_register(downto_value, temp_reg, ignore_iterator=idd)
        pre_run_code += "\nSUB {} {}".format(counter_reg, temp_reg)
        pre_run_code += "\n" + self.__put_address_to_register(Identifier(counter), temp_reg, initialize=True)

        code = "JZERO {}".format(counter_reg) + " {}"
        code += "\nSTORE {} {}".format(counter_reg, temp_reg)
        code += "\n" + commands_code
        code += "\n" + self.__generate_constant(self.variable_table.get_address(idd), temp_reg)
        code += "\nLOAD {} {}".format(iterator_reg, temp_reg)
        code += "\nDEC {}".format(iterator_reg)
        code += "\nSTORE {} {}".format(iterator_reg, temp_reg)
        code += "\n" + self.__put_address_to_register(Identifier(counter), temp_reg)
        code += "\nLOAD {} {}".format(counter_reg, temp_reg)
        code += "\nDEC {}".format(counter_reg)
        code += "\nJUMP {}".format(-self.__line_count(code))
        code = code.format(self.__line_count(code))

        self.variable_table.remove_iterator(idd)
        self.variable_table.remove_variable(counter)
        return pre_run_code + "\n" + code

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
            code += "\n" + self.__generate_constant(self.variable_table.get_marker(), reg2)
            code += "\nSTORE {} {}".format(reg, reg2)
            code += "\nPUT {}".format(reg2)
        else:
            code = self.__put_address_to_register(val.core, register=reg)
            code += "\nPUT {}".format(reg)
        return code
