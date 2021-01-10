from model.nonterminals.Identifier import Identifier
from model.nonterminals.Expression import Expression
from model.nonterminals.Value import Value


class Assign:

    def __init__(self, changed_identifier: Identifier, assigned_expression: Expression, lineno: int = None):
        self.lineno = lineno
        self.changed_identifier = changed_identifier
        self.assigned_expression = assigned_expression

    def __str__(self):
        return "{} := {}".format(self.changed_identifier, self.assigned_expression)

    def __repr__(self):
        return str(self)

    def get_changed_identifiers(self):
        return [self.changed_identifier]
