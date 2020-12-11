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
    DO = r"DO"
    REPEAT = r"REPEAT"
    UNTIL = r"UNTIL"
    FOR = r"FOR"
    FROM = r"FROM"
    DOWNTO = r"DOWNTO"
    TO = r"TO"
    READ = r"READ"
    WRITE = r"WRITE"

    ASGN = r":="
    NEQ = r"!="
    EQ = r"="
    LEQ = r"<="
    GEQ = r">="
    LT = r"<"
    GT = r">"
    ID = r"[_a-z]+"

    literals = (
        "+", "-", "*", "/", "%",
        ",", "(", ")", ":", ";"
    )

    ignore = " \t\n"

    @_(r'\[[^\[\]*]\]')
    def comment(self, t):
        pass

    @_(r'[0-9]+')
    def NUM(self, t):
        t.value = int(t.value)
        return t


def test():
    lexer = LangLexer()
    text = """var := 32;
IF var <= 32 THEN READ a ELSE READ b ENDIF"""
    for t in lexer.tokenize(text):
        print(t)


if __name__ == "__main__":
    test()
