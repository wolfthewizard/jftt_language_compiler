from core.LangLexer import LangLexer
from core.LangParser import LangParser
from core.LangTranslator import LangTranslator
from core.LangRegisterMachine import LangRegisterMachine
from core.LangVariableTable import LangVariableTable
from core.GenericTranslator import GenericTranslator
from core.OperationTranslator import OperationTranslator
from core.ConditionTranslator import ConditionTranslator
import sys
from model.errors import CodeException


def main(argv):
    if len(argv) == 1:
        print("""Usage:
kompilator source_file destination_file
The compiler will compile source code from source_file into assembly form and put it into destination_file.""")
        exit(0)

    if len(argv) != 3:
        print("Invalid number of arguments.")
        exit(1)

    try:
        with open(argv[1], "r") as f:
            source = f.read()
    except FileNotFoundError:
        print("Source file does not exist.")
        exit(1)

    lexer = LangLexer()
    parser = LangParser()

    variable_table = LangVariableTable()
    register_machine = LangRegisterMachine()
    generic_translator = GenericTranslator(variable_table, register_machine)
    operation_translator = OperationTranslator(variable_table, register_machine, generic_translator)
    condition_translator = ConditionTranslator(variable_table, register_machine, generic_translator)
    lang_translator = LangTranslator(variable_table, register_machine, operation_translator, condition_translator,
                                     generic_translator)

    tokens = lexer.tokenize(source)
    program = parser.parse(tokens)
    try:
        assembly = lang_translator.translate_program(program)
        with open(argv[2], "w") as f:
            f.write(assembly)
    except CodeException as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main(sys.argv)
