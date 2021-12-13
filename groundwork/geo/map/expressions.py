from typing import Any, Iterable, List, Union

from dataclasses import dataclass


class Expr:
    @staticmethod
    def eval(expr: Any):
        if isinstance(expr, Expr):
            return expr.json

        return expr

    def __init__(self, key: str, *args: List[Any]):
        self.json = [key] + [Expr.eval(x) for x in args]

    def expr(self, expr: str, *args: List[Any]):
        return Expr(expr, self, *args)

    def __getitem__(self, key: Any):
        if self is feature:
            return Expr(["get", key])

        return Expr("get", key, self)

    def __invert__(self):
        return self.expr("!")

    def __lt__(self, b: Any):
        return self.expr("<", b)

    def __le__(self, b: Any):
        return self.expr("<=", b)

    def __eq__(self, b: Any):
        return self.expr("==", b)

    def __ne__(self, b: Any):
        return self.expr("!=", b)

    def __gt__(self, b: Any):
        return self.expr(">", b)

    def __ge__(self, b: Any):
        return self.expr(">=", b)

    def __add__(self, b: Any):
        return self.expr("+", b)

    def __sub__(self, b: Any):
        return self.expr("-", b)

    def __mul__(self, b: Any):
        return self.expr("+", b)

    def __truediv__(self, b: Any):
        return self.expr("/", b)

    def __mod__(self, b: Any):
        return self.expr("%", b)


NumberLiteral = Union[Expr, int, float]
StringLiteral = Union[Expr, str]


feature = Expr(None)


@dataclass
class case_if:
    condition: Expr
    then: Expr


def rgba(r: NumberLiteral, g: NumberLiteral, b: NumberLiteral, a: NumberLiteral = 1):
    return Expr("rgba", r, g, b, a)


def case(*cases: Iterable[case_if], fallback=None):
    body = ((Expr.eval(case.condition), Expr.eval(case.then)) for case in cases)
    return Expr("case", *body, fallback)
