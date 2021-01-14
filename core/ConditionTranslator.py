from core.LangVariableTable import LangVariableTable
from core.LangRegisterMachine import LangRegisterMachine
from core.GenericTranslator import GenericTranslator
from model.nonterminals.Value import Value


class ConditionTranslator:

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
        # if left_val.is_int() and right_val.is_int():
        #     pass
        # else:
        #     pass
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        condition_reg = self.register_machine.borrow_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\n" + self.generic_translator.copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP 5"
        code += "\n" + self.generic_translator.copy_register(reg2, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg1)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP {}"
        return code

    def __perform_inequality(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        condition_reg = self.register_machine.borrow_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\n" + self.generic_translator.copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP 7"
        code += "\n" + self.generic_translator.copy_register(reg2, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg1)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP 2"
        code += "\nJUMP {}"
        return code

    def __perform_less(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        condition_reg = self.register_machine.borrow_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\n" + self.generic_translator.copy_register(reg2, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg1)
        code += "\nJZERO {}".format(condition_reg) + " {}"
        return code

    def __perform_more(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        condition_reg = self.register_machine.borrow_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\n" + self.generic_translator.copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {}".format(condition_reg) + " {}"
        return code

    def __perform_less_equal(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        condition_reg = self.register_machine.borrow_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\n" + self.generic_translator.copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP {}"
        return code

    def __perform_more_equal(self, left_val: Value, right_val: Value):
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        condition_reg = self.register_machine.borrow_register()

        code = self.generic_translator.put_value_to_register(left_val, reg1)
        code += "\n" + self.generic_translator.put_value_to_register(right_val, reg2)
        code += "\n" + self.generic_translator.copy_register(reg2, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg1)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP {}"
        return code
