import sympy as sp


class MathEngine:
    def __init__(self):
        self.tokens = []

    def add_token(self, token):
        if token is None:
            return

        self.tokens.append(token)

    def remove_last_token(self):
        if self.tokens:
            return self.tokens.pop()

        return None

    def clear(self):
        self.tokens.clear()

    def get_tokens(self):
        return self.tokens.copy()

    def get_display_expression(self):
        return "".join(self.tokens)

    def build_expression(self):
        expression = self.get_display_expression()

        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        expression = expression.replace("²", "**2")

        return expression

    def parse(self):
        expression = self.build_expression()

        if not expression:
            return None

        try:
            return sp.sympify(
                expression,
                locals={"x": sp.Symbol("x")}
            )
        except (sp.SympifyError, ValueError, TypeError):
            return None

    def simplify(self):
        expression = self.parse()

        if expression is None:
            return None

        return sp.simplify(expression)

    def is_equivalent(self, target_expression):
        current_expression = self.parse()

        if current_expression is None:
            return False

        try:
            target = sp.sympify(
                target_expression,
                locals={"x": sp.Symbol("x")}
            )

            difference = sp.simplify(
                current_expression - target
            )

            return difference == 0

        except (sp.SympifyError, ValueError, TypeError):
            return False