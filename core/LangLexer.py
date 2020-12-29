from sly import Lexer


class LangLexer(Lexer):

    tokens = (
        NUM,
        ID,
        ASGN,
        EQ, NEQ, LT, GT, LEQ, GEQ,

        DECLARE, BEGIN, END,
        IF, THEN, ELSE, ENDIF,
        WHILE, DO, ENDWHILE,
        REPEAT, UNTIL,
        FOR, FROM, TO, DOWNTO, ENDFOR,
        READ, WRITE
    )

    DECLARE = r"DECLARE"
    BEGIN = r"BEGIN"
    ENDWHILE = r"ENDWHILE"
    ENDFOR = r"ENDFOR"
    ENDIF = r"ENDIF"
    END = r"END"
    IF = r"IF"
    THEN = r"THEN"
    ELSE = r"ELSE"
    WHILE = r"WHILE"
    DOWNTO = r"DOWNTO"
    DO = r"DO"
    REPEAT = r"REPEAT"
    UNTIL = r"UNTIL"
    FOR = r"FOR"
    FROM = r"FROM"
    TO = r"TO"
    READ = r"READ"
    WRITE = r"WRITE"

    ASGN = r":="
    NEQ = r"!="
    LEQ = r"<="
    GEQ = r">="
    EQ = r"="
    LT = r"<"
    GT = r">"
    ID = r"[_a-z]+"

    literals = (
        "+", "-", "*", "/", "%",
        ",", "(", ")", ":", ";"
    )

    ignore = " \t"

    @_(r'\n')
    def line_count(self, t):
        self.lineno += 1

    @_(r'\[[^\[\]]*\]')
    def comment(self, t):
        self.lineno += t.value.count("\n")

    @_(r'[0-9]+')
    def NUM(self, t):
        t.value = int(t.value)
        return t

    def error(self, t):
        print("error at line {}: bad character - {}".format(self.lineno, t.value[0]))
        exit(1)


def test():
    lexer = LangLexer()
    text = """var := 32;
IF var <= 32 THEN READ a ELSE READ b ENDIF"""
    for t in lexer.tokenize(text):
        print(t)


if __name__ == "__main__":
    test()
