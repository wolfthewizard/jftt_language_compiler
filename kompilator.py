from LangLexer import LangLexer
from LangParser import LangParser
import sys


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

    assembly = parser.parse(lexer.tokenize(source))

    with open(argv[2], "w") as f:
        f.write(assembly)


if __name__ == "__main__":
    main(sys.argv)
