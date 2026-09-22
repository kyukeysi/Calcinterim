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
        expression = expression.replace("^", "**")
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

    def calculate(self):
        expression = self.parse()

        if expression is None:
            return None

        try:
            return sp.simplify(expression)
        except (sp.SympifyError, ValueError, TypeError):
            return None

    def get_answer_text(self):
        answer = self.calculate()

        if answer is None:
            return None

        return str(answer)

    def simplify(self):
        return self.calculate()

    def integrate(self):
        expression = self.parse()

        if expression is None:
            return None

        try:
            x = sp.Symbol("x")

            return sp.simplify(
                sp.integrate(expression, x)
            )
        except (sp.SympifyError, ValueError, TypeError):
            return None

    def get_integral_text(self):
        integral = self.integrate()

        if integral is None:
            return None

        return f"{integral} + C"

    def definite_integral(self, lower_bound, upper_bound):
        expression = self.parse()

        if expression is None:
            return None

        try:
            x = sp.Symbol("x")

            result = sp.integrate(
                expression,
                (x, lower_bound, upper_bound)
            )

            return sp.simplify(result)

        except (sp.SympifyError, ValueError, TypeError):
            return None

    def get_definite_integral_text(
        self,
        lower_bound,
        upper_bound
    ):
        result = self.definite_integral(
            lower_bound,
            upper_bound
        )

        if result is None:
            return None

        return str(result)

    def get_definite_integral_steps(
        self,
        lower_bound,
        upper_bound
    ):
        expression = self.parse()

        if expression is None:
            return None

        try:
            x = sp.Symbol("x")

            antiderivative = sp.simplify(
                sp.integrate(expression, x)
            )

            lower_result = sp.simplify(
                antiderivative.subs(
                    x,
                    lower_bound
                )
            )

            upper_result = sp.simplify(
                antiderivative.subs(
                    x,
                    upper_bound
                )
            )

            result = sp.simplify(
                upper_result - lower_result
            )

            return {
                "integrand": expression,
                "antiderivative": antiderivative,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "lower_result": lower_result,
                "upper_result": upper_result,
                "result": result
            }

        except (
            sp.SympifyError,
            ValueError,
            TypeError
        ):
            return None

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