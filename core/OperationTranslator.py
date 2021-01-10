from core.LangVariableTable import LangVariableTable
from core.LangRegisterMachine import LangRegisterMachine
from core.GenericTranslator import GenericTranslator
from model.nonterminals.Value import Value
from model.nonterminals.Identifier import Identifier
from model.internal.Feedback import Feedback


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


class OperationTranslator:

    ADDITION_SWITCH_THRESHOLD = 10
    MULTIPLICATION_SWITCH_THRESHOLD = 1_000_000

    def __init__(self, variable_table: LangVariableTable, register_machine: LangRegisterMachine,
                 generic_translator: GenericTranslator):
        self.variable_table = variable_table
        self.register_machine = register_machine
        self.generic_translator = generic_translator

    def perform_operation(self, left_val: Value, right_val: Value, operation: str,
                          changed_identifier: Identifier) -> Feedback:
        if operation == "+":
            return self.__perform_addition(left_val, right_val, changed_identifier)
        elif operation == "-":
            return self.__perform_subtraction(left_val, right_val, changed_identifier)
        elif operation == "*":
            return self.__perform_multiplication(left_val, right_val, changed_identifier)
        elif operation == "/":
            return self.__perform_division(left_val, right_val, changed_identifier)
        else:
            return self.__perform_modulo(left_val, right_val, changed_identifier)

    def __perform_addition(self, left_val: Value, right_val: Value, changed_identifier: Identifier) -> Feedback:
        if left_val.is_int() and right_val.is_int():
            result = left_val.core + right_val.core
            self.variable_table.set_value(result, changed_identifier.name, changed_identifier.offset)
            reg = self.register_machine.fetch_register()
            code = self.generic_translator.generate_constant(result, reg)
            return Feedback(code, reg)
        elif left_val.is_int() or right_val.is_int():
            self.variable_table.set_value(None, changed_identifier.name, changed_identifier.offset)
            if left_val.is_int():
                num = left_val.core
                val = right_val
            else:
                num = right_val.core
                val = left_val
            if num > OperationTranslator.ADDITION_SWITCH_THRESHOLD:
                return self.__perform_addition_2i(left_val, right_val)
            reg = self.register_machine.fetch_register()
            code = self.generic_translator.put_value_to_register(val, reg)
            code += "\n" + "\n".join(["INC {}".format(reg) for _ in range(num)])
            return Feedback(code, reg)
        else:
            self.variable_table.set_value(None, changed_identifier.name, changed_identifier.offset)
            if left_val == right_val:
                reg = self.register_machine.fetch_register()
                code = self.generic_translator.put_value_to_register(left_val, reg)
                code += "\nSHL {}".format(reg)
                return Feedback(code, reg)
            else:
                return self.__perform_addition_2i(left_val, right_val)

    def __perform_addition_2i(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\nADD {} {}".format(reg1, reg2)
        return Feedback(code, reg1)

    def __perform_subtraction(self, left_val: Value, right_val: Value, changed_identifier: Identifier) -> Feedback:
        if left_val.is_int() and right_val.is_int():
            result = abs(left_val.core - right_val.core)
            self.variable_table.set_value(result, changed_identifier.name, changed_identifier.offset)
            reg = self.register_machine.fetch_register()
            code = self.generic_translator.generate_constant(result, reg)
            return Feedback(code, reg)
        elif right_val.is_int():
            self.variable_table.set_value(None, changed_identifier.name, changed_identifier.offset)
            num = right_val.core
            if num > OperationTranslator.ADDITION_SWITCH_THRESHOLD:
                return self.__perform_subtraction_2i(left_val, right_val)
            reg = self.register_machine.fetch_register()
            code = self.generic_translator.put_value_to_register(left_val, reg)
            code += "\n" + "\n".join(["DEC {}".format(reg) for _ in range(num)])
            return Feedback(code, reg)
        else:
            if not left_val.is_int() and left_val == right_val:
                self.variable_table.set_value(0, changed_identifier.name, changed_identifier.offset)
                reg = self.register_machine.fetch_register()
                code = "RESET {}".format(reg)
                return Feedback(code, reg)
            else:
                self.variable_table.set_value(None, changed_identifier.name, changed_identifier.offset)
                return self.__perform_subtraction_2i(left_val, right_val)

    def __perform_subtraction_2i(self, left_val: Value, right_val: Value) -> Feedback:
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\nSUB {} {}".format(reg1, reg2)
        return Feedback(code, reg1)

    def __perform_multiplication(self, left_val: Value, right_val: Value, changed_identifier: Identifier) -> Feedback:
        if left_val.is_int() and right_val.is_int():
            result = left_val.core * right_val.core
            self.variable_table.set_value(result, changed_identifier.name, changed_identifier.offset)
            reg = self.register_machine.fetch_register()
            code = self.generic_translator.generate_constant(result, reg)
            return Feedback(code, reg)
        elif left_val.is_int() or right_val.is_int():
            self.variable_table.set_value(None, changed_identifier.name, changed_identifier.offset)
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
            elif num == 1:
                reg = self.register_machine.fetch_register()
                code = self.generic_translator.put_value_to_register(val, reg)
                return Feedback(code, reg)
            elif num < OperationTranslator.MULTIPLICATION_SWITCH_THRESHOLD and is_power_of_two(num):
                reg = self.register_machine.fetch_register()
                code = self.generic_translator.put_value_to_register(val, reg)
                code += "\n" + "\n".join(["SHL {}".format(reg) for _ in range(log(num))])
                return Feedback(code, reg)
            else:
                return self.__perform_multiplication_2i(left_val, right_val)
        else:
            self.variable_table.set_value(None, changed_identifier.name, changed_identifier.offset)
            return self.__perform_multiplication_2i(left_val, right_val)

    def __perform_multiplication_2i(self, left_val: Value, right_val: Value) -> Feedback:
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        helper_reg = self.register_machine.borrow_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\n" + self.generic_translator.copy_register(source_reg=reg2, dest_reg=helper_reg)
        code += "\nSUB {} {}".format(helper_reg, reg1)
        code += "\nJZERO {} 7".format(helper_reg)
        code += "\n" + self.generic_translator.copy_register(source_reg=reg2, dest_reg=helper_reg)
        code += "\n" + self.generic_translator.copy_register(source_reg=reg1, dest_reg=reg2)
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

    def __perform_division(self, left_val: Value, right_val: Value, changed_identifier: Identifier) -> Feedback:
        if left_val.is_int() and right_val.is_int():
            result = left_val.core // right_val.core if right_val.core != 0 else 0
            self.variable_table.set_value(result, changed_identifier.name, changed_identifier.offset)
            reg = self.register_machine.fetch_register()
            code = self.generic_translator.generate_constant(result, reg)
            return Feedback(code, reg)
        elif right_val.is_int():
            self.variable_table.set_value(None, changed_identifier.name, changed_identifier.offset)
            num = right_val.core
            if num == 0:
                reg = self.register_machine.fetch_register()
                code = "RESET {}".format(reg)
                return Feedback(code, reg)
            elif num < OperationTranslator.MULTIPLICATION_SWITCH_THRESHOLD and is_power_of_two(num):
                reg = self.register_machine.fetch_register()
                code = self.generic_translator.put_value_to_register(left_val, reg)
                code += "\n" + "\n".join(["SHR {}".format(reg) for _ in range(log(num))])
                return Feedback(code, reg)
            else:
                return self.__perform_division_2i(left_val, right_val)
        else:
            self.variable_table.set_value(None, changed_identifier.name, changed_identifier.offset)
            if not left_val.is_int() and left_val == right_val:
                reg = self.register_machine.fetch_register()
                helper_reg = self.register_machine.fetch_register()
                code = self.generic_translator.put_value_to_register(left_val, helper_reg)
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

        code = self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\nRESET {}".format(reg1)
        code += "\nJZERO {}".format(reg2)                       # END
        snippet = self.generic_translator.put_value_to_register(left_val, dividend_reg)
        code += " {}".format(31 + self.generic_translator.line_count(snippet))
        code += "\n" + snippet
        code += "\nRESET {}".format(mult_reg)
        code += "\nINC {}".format(mult_reg)
        code += "\n" + self.generic_translator.copy_register(reg2, check_reg)
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

    def __perform_modulo(self, left_val: Value, right_val: Value, changed_identifier: Identifier) -> Feedback:
        if left_val.is_int() and right_val.is_int():
            result = left_val.core % right_val.core if right_val.core != 0 else 0
            self.variable_table.set_value(result, changed_identifier.name, changed_identifier.offset)
            reg = self.register_machine.fetch_register()
            code = self.generic_translator.generate_constant(result, reg)
            return Feedback(code, reg)
        elif right_val.is_int():
            self.variable_table.set_value(None, changed_identifier.name, changed_identifier.offset)
            num = right_val.core
            if num == 0 or num == 1:
                reg = self.register_machine.fetch_register()
                code = "RESET {}".format(reg)
                return Feedback(code, reg)
            elif num == 2:
                reg = self.register_machine.fetch_register()
                code = self.generic_translator.put_value_to_register(left_val, reg)
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
                self.variable_table.set_value(0, changed_identifier.name, changed_identifier.offset)
                reg = self.register_machine.fetch_register()
                code = "RESET {}".format(reg)
                return Feedback(code, reg)
            else:
                self.variable_table.set_value(None, changed_identifier.name, changed_identifier.offset)
                return self.__perform_modulo_2i(left_val, right_val)

    def __perform_modulo_2i(self, left_val: Value, right_val: Value) -> Feedback:
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        check_reg, mult_reg, division_result_reg = self.register_machine.borrow_registers(3)

        code = self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\nRESET {}".format(division_result_reg)
        code += "\nJZERO {}".format(reg2)  # END
        snippet = self.generic_translator.put_value_to_register(left_val, reg1)
        code += " {}".format(31 + self.generic_translator.line_count(snippet))
        code += "\n" + snippet
        code += "\nRESET {}".format(mult_reg)
        code += "\nINC {}".format(mult_reg)
        code += "\n" + self.generic_translator.copy_register(reg2, check_reg)
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
