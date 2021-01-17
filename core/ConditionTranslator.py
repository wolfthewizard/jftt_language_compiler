from core.LangVariableTable import LangVariableTable
from core.LangRegisterMachine import LangRegisterMachine
from core.GenericTranslator import GenericTranslator
from model.nonterminals.Value import Value


class ConditionTranslator:

    EQUALITY_SWITCH_THRESHOLD = 12
    SUPERIORITY_SWITCH_THRESHOLD = 4

    def __init__(self, variable_table: LangVariableTable, register_machine: LangRegisterMachine,
                 generic_translator: GenericTranslator):
        self.variable_table = variable_table
        self.register_machine = register_machine
        self.generic_translator = generic_translator

    def perform_comparison(self, left_val: Value, right_val: Value, comparison: str) -> str:
        if comparison == "=":
            return self.__perform_equality(left_val, right_val)
        elif comparison == "!=":
            return self.__perform_inequality(left_val, right_val)
        elif comparison == "<":
            return self.__perform_less(left_val, right_val)
        elif comparison == ">":
            return self.__perform_more(left_val, right_val)
        elif comparison == "<=":
            return self.__perform_less_equal(left_val, right_val)
        else:
            return self.__perform_more_equal(left_val, right_val)

    def __perform_equality(self, left_val: Value, right_val: Value):
        if left_val.is_int() and right_val.is_int():
            met = left_val.core == right_val.core
            if met:
                code = "JUMP 1"
            else:
                code = "JUMP {}"
        elif left_val.is_int() or right_val.is_int():
            if left_val.is_int():
                num = left_val.core
                val = right_val
            else:
                num = right_val.core
                val = left_val

            if num <= ConditionTranslator.EQUALITY_SWITCH_THRESHOLD:
                reg = self.register_machine.fetch_register()
                code = self.generic_translator.put_value_to_register(val, reg)
                while num > 0:
                    code += "\nJZERO {} {}".format(reg, 2 * num + 1)
                    code += "\nDEC {}".format(reg)
                    num -= 1
                code += "\nJZERO {} 2".format(reg)
                code += "\nJUMP {}"
            else:
                code = self.__perform_equality_2i(left_val, right_val)
        else:
            code = self.__perform_equality_2i(left_val, right_val)
        return code

    def __perform_equality_2i(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        condition_reg = self.register_machine.borrow_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\n" + self.generic_translator.copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP 3"
        code += "\nSUB {} {}".format(reg2, reg1)
        code += "\nJZERO {} 2".format(reg2)
        code += "\nJUMP {}"

        return code

    def __perform_inequality(self, left_val: Value, right_val: Value):
        if left_val.is_int() and right_val.is_int():
            met = left_val.core != right_val.core
            if met:
                code = "JUMP 1"
            else:
                code = "JUMP {}"
        elif left_val.is_int() or right_val.is_int():
            if left_val.is_int():
                num = left_val.core
                val = right_val
            else:
                num = right_val.core
                val = left_val

            if num <= ConditionTranslator.EQUALITY_SWITCH_THRESHOLD:
                reg = self.register_machine.fetch_register()
                code = self.generic_translator.put_value_to_register(val, reg)
                while num > 0:
                    code += "\nJZERO {} {}".format(reg, 2 * num + 3)
                    code += "\nDEC {}".format(reg)
                    num -= 1
                code += "\nJZERO {} 2".format(reg)
                code += "\nJUMP 2"
                code += "\nJUMP {}"
            else:
                code = self.__perform_inequality_2i(left_val, right_val)
        else:
            code = self.__perform_inequality_2i(left_val, right_val)
        return code

    def __perform_inequality_2i(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        condition_reg = self.register_machine.borrow_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\n" + self.generic_translator.copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP 5"
        code += "\nSUB {} {}".format(reg2, reg1)
        code += "\nJZERO {} 2".format(reg2)
        code += "\nJUMP 2"
        code += "\nJUMP {}"
        return code

    def __perform_less(self, left_val: Value, right_val: Value):
        if left_val.is_int() and right_val.is_int():
            met = left_val.core < right_val.core
            if met:
                code = "JUMP 1"
            else:
                code = "JUMP {}"
        elif left_val.is_int():
            code = self.__perform_more(right_val, left_val)
        elif right_val.is_int() and right_val.core <= ConditionTranslator.SUPERIORITY_SWITCH_THRESHOLD:
            num = right_val.core
            reg = self.register_machine.fetch_register()
            code = self.generic_translator.put_value_to_register(left_val, reg)
            while num > 0:
                code += "\nJZERO {} {}".format(reg, 2 * num + 1)
                code += "\nDEC {}".format(reg)
                num -= 1
            code += "\nJUMP {}"
        else:
            code = self.__perform_less_2i(left_val, right_val)
        return code

    def __perform_less_2i(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\nSUB {} {}".format(reg2, reg1)
        code += "\nJZERO {}".format(reg2) + " {}"
        return code

    def __perform_more(self, left_val: Value, right_val: Value):
        if left_val.is_int() and right_val.is_int():
            met = left_val.core > right_val.core
            if met:
                code = "JUMP 1"
            else:
                code = "JUMP {}"
        elif left_val.is_int():
            code = self.__perform_less(right_val, left_val)
        elif right_val.is_int() and right_val.core <= ConditionTranslator.SUPERIORITY_SWITCH_THRESHOLD:
            num = right_val.core
            reg = self.register_machine.fetch_register()
            code = self.generic_translator.put_value_to_register(left_val, reg)
            while num > 0:
                code += "\nJZERO {} {}".format(reg, 2 * num)
                code += "\nDEC {}".format(reg)
                num -= 1
            code += "\nJZERO {}".format(reg) + " {}"
        else:
            code = self.__perform_more_2i(left_val, right_val)
        return code

    def __perform_more_2i(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\nSUB {} {}".format(reg1, reg2)
        code += "\nJZERO {}".format(reg1) + " {}"
        return code

    def __perform_less_equal(self, left_val: Value, right_val: Value):
        if left_val.is_int() and right_val.is_int():
            met = left_val.core <= right_val.core
            if met:
                code = "JUMP 1"
            else:
                code = "JUMP {}"
        elif left_val.is_int():
            code = self.__perform_more_equal(right_val, left_val)
        elif right_val.is_int() and right_val.core <= ConditionTranslator.SUPERIORITY_SWITCH_THRESHOLD:
            num = right_val.core
            reg = self.register_machine.fetch_register()
            code = self.generic_translator.put_value_to_register(left_val, reg)
            while num > 0:
                code += "\nJZERO {} {}".format(reg, 2 * num + 2)
                code += "\nDEC {}".format(reg)
                num -= 1
            code += "\nJZERO {} 2".format(reg)
            code += "\nJUMP {}"
        else:
            code = self.__perform_less_equal_2i(left_val, right_val)
        return code

    def __perform_less_equal_2i(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\nSUB {} {}".format(reg1, reg2)
        code += "\nJZERO {} 2".format(reg1)
        code += "\nJUMP {}"
        return code

    def __perform_more_equal(self, left_val: Value, right_val: Value):
        if left_val.is_int() and right_val.is_int():
            met = left_val.core >= right_val.core
            if met:
                code = "JUMP 1"
            else:
                code = "JUMP {}"
        elif left_val.is_int():
            code = self.__perform_less_equal(right_val, left_val)
        elif right_val.is_int() and right_val.core <= ConditionTranslator.SUPERIORITY_SWITCH_THRESHOLD:
            num = right_val.core
            reg = self.register_machine.fetch_register()
            code = self.generic_translator.put_value_to_register(left_val, reg)
            while num > 0:
                code += "\nJZERO {} {}".format(reg, 2 * num + 1)
                code += "\nDEC {}".format(reg)
                num -= 1
            code += "\nJUMP 2"
            code += "\nJUMP {}"
        else:
            code = self.__perform_more_equal2i(left_val, right_val)
        return code

    def __perform_more_equal2i(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\nSUB {} {}".format(reg2, reg1)
        code += "\nJZERO {} 2".format(reg2)
        code += "\nJUMP {}"
        return code
