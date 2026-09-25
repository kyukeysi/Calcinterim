import random


EASY_PROBLEMS = [
    {
        "display": "2 + 3 = ?",
        "answer": 5,
        "type": "easy",
    },
    {
        "display": "4 x 5 + 2 / 2 = ?",
        "answer": 21,
        "type": "easy",
    },
    {
        "display": "10 - 6^4 = ?",
        "answer": -1286,
        "type": "easy",
    },
    {
        "display": "9 / 3 = ?",
        "answer": 3,
        "type": "easy",
    },
    {
        "display": "3 + 7 = ?",
        "answer": 10,
        "type": "easy",
    },
    {
        "display": "8 x 3 = ?",
        "answer": 24,
        "type": "easy",
    },
    {
        "display": "15 - 8 = ?",
        "answer": 7,
        "type": "easy",
    },
    {
        "display": "6 x 6 = ?",
        "answer": 36,
        "type": "easy",
    },
    {
        "display": "20 / 4 = ?",
        "answer": 5,
        "type": "easy",
    },
    {
        "display": "5 x 6 + 9 = ?",
        "answer": 39,
        "type": "easy",
    },
    {
        "display": "12 - 4 / 2= ?",
        "answer": 10,
        "type": "easy",
    },
    {
        "display": "(2 + 3) x 4 = ?",
        "answer": 20,
        "type": "easy",
    },
    {
        "display": "7 x 8 = ?",
        "answer": 56,
        "type": "easy",
    },
    {
        "display": "18 / 6 = ?",
        "answer": 3,
        "type": "easy",
    },
    {
        "display": "11 + 13 = ?",
        "answer": 24,
        "type": "easy",
    },
    {
        "display": "3^2 = ?",
        "answer": 9,
        "type": "easy",
    },
    {
        "display": "2^4 = ?",
        "answer": 16,
        "type": "easy",
    },
    {
        "display": "(5 + 3) x 2 = ?",
        "answer": 16,
        "type": "easy",
    },
    {
        "display": "100 - 37 = ?",
        "answer": 63,
        "type": "easy",
    },
    {
        "display": "4 x (3 + 2) = ?",
        "answer": 20,
        "type": "easy",
    },
]


CHALLENGE_PROBLEMS = [
    {
        "integrand": "3",
        "lower_bound": 1,
        "upper_bound": 4,
        "answer": 9,
        "display": "integral 1->4 of 3 dx",
        "type": "hard",
    },
    {
        "integrand": "2x",
        "lower_bound": 1,
        "upper_bound": 3,
        "answer": 8,
        "display": "integral 1->3 of 2x dx",
        "type": "hard",
    },
    {
        "integrand": "x^2",
        "lower_bound": 0,
        "upper_bound": 3,
        "answer": 9,
        "display": "integral 0->3 of x^2 dx",
        "type": "hard",
    },
    {
        "integrand": "4x",
        "lower_bound": 0,
        "upper_bound": 5,
        "answer": 50,
        "display": "integral 0->5 of 4x dx",
        "type": "hard",
    },
    {
        "integrand": "x^2+1",
        "lower_bound": 0,
        "upper_bound": 3,
        "answer": 12,
        "display": "integral 0->3 of (x^2+1) dx",
        "type": "hard",
    },
    {
        "integrand": "6x^2",
        "lower_bound": 1,
        "upper_bound": 2,
        "answer": 14,
        "display": "integral 1->2 of 6x^2 dx",
        "type": "hard",
    },
    {
        "integrand": "3x^2+2x",
        "lower_bound": 0,
        "upper_bound": 2,
        "answer": 12,
        "display": "integral 0->2 of (3x^2+2x) dx",
        "type": "hard",
    },
    {
        "integrand": "x^3",
        "lower_bound": 0,
        "upper_bound": 2,
        "answer": 4,
        "display": "integral 0->2 of x^3 dx",
        "type": "hard",
    },
    {
        "integrand": "5",
        "lower_bound": 2,
        "upper_bound": 8,
        "answer": 30,
        "display": "integral 2->8 of 5 dx",
        "type": "hard",
    },
    {
        "integrand": "2x+3",
        "lower_bound": 1,
        "upper_bound": 5,
        "answer": 36,
        "display": "integral 1->5 of (2x+3) dx",
        "type": "hard",
    },
]


HARD_PROBLEMS = [
    {
        "display": "2 + 2",
        "answer": 4,
        "type": "hard",
        "required_op": "MULTIPLICATION",
        "required_symbols": ["*", "×", "x", "(", ")"],
        "instruction": "Get the answer by using MULTIPLICATION (x or ())",
    },
    {
        "display": "3 + 3",
        "answer": 6,
        "type": "hard",
        "required_op": "MULTIPLICATION",
        "required_symbols": ["*", "×", "x", "(", ")"],
        "instruction": "Get the answer by using MULTIPLICATION (x or ())",
    },
    {
        "display": "4 + 4",
        "answer": 8,
        "type": "hard",
        "required_op": "MULTIPLICATION",
        "required_symbols": ["*", "×", "x", "(", ")"],
        "instruction": "Get the answer by using MULTIPLICATION (x or ())",
    },
    {
        "display": "5 + 5",
        "answer": 10,
        "type": "hard",
        "required_op": "MULTIPLICATION",
        "required_symbols": ["*", "×", "x", "(", ")"],
        "instruction": "Get the answer by using MULTIPLICATION (x or ())",
    },
    {
        "display": "6 + 6",
        "answer": 12,
        "type": "hard",
        "required_op": "MULTIPLICATION",
        "required_symbols": ["*", "×", "x", "(", ")"],
        "instruction": "Get the answer by using MULTIPLICATION (x or ())",
    },
    {
        "display": "8 + 8",
        "answer": 16,
        "type": "hard",
        "required_op": "MULTIPLICATION",
        "required_symbols": ["*", "×", "x", "(", ")"],
        "instruction": "Get the answer by using MULTIPLICATION (x or ())",
    },
    {
        "display": "10 + 10",
        "answer": 20,
        "type": "hard",
        "required_op": "MULTIPLICATION",
        "required_symbols": ["*", "×", "x", "(", ")"],
        "instruction": "Get the answer by using MULTIPLICATION (x or ())",
    },
    {
        "display": "3 x 3",
        "answer": 9,
        "type": "hard",
        "required_op": "ADDITION",
        "required_symbols": ["+"],
        "instruction": "Get the answer by using ADDITION",
    },
    {
        "display": "4 x 2",
        "answer": 8,
        "type": "hard",
        "required_op": "ADDITION",
        "required_symbols": ["+"],
        "instruction": "Get the answer by using ADDITION",
    },
    {
        "display": "5 x 2",
        "answer": 10,
        "type": "hard",
        "required_op": "ADDITION",
        "required_symbols": ["+"],
        "instruction": "Get the answer by using ADDITION",
    },
    {
        "display": "3 x 4",
        "answer": 12,
        "type": "hard",
        "required_op": "ADDITION",
        "required_symbols": ["+"],
        "instruction": "Get the answer by using ADDITION",
    },
    {
        "display": "4 x 4",
        "answer": 16,
        "type": "hard",
        "required_op": "ADDITION",
        "required_symbols": ["+"],
        "instruction": "Get the answer by using ADDITION",
    },
    {
        "display": "5 x 3",
        "answer": 15,
        "type": "hard",
        "required_op": "ADDITION",
        "required_symbols": ["+"],
        "instruction": "Get the answer by using ADDITION",
    },
    {
        "display": "6 x 2",
        "answer": 12,
        "type": "hard",
        "required_op": "SUBTRACTION",
        "required_symbols": ["-"],
        "instruction": "Get the answer by using SUBTRACTION",
    },
    {
        "display": "20 - 10",
        "answer": 10,
        "type": "hard",
        "required_op": "MULTIPLICATION",
        "required_symbols": ["*", "×", "x", "(", ")"],
        "instruction": "Get the answer by using MULTIPLICATION (x or ())",
    },
    {
        "display": "15 - 9",
        "answer": 6,
        "type": "hard",
        "required_op": "MULTIPLICATION",
        "required_symbols": ["*", "×", "x", "(", ")"],
        "instruction": "Get the answer by using MULTIPLICATION (x or ())",
    },
    {
        "display": "25 - 9",
        "answer": 16,
        "type": "hard",
        "required_op": "MULTIPLICATION",
        "required_symbols": ["*", "×", "x", "(", ")"],
        "instruction": "Get the answer by using MULTIPLICATION (x or ())",
    },
    {
        "display": "20 - 5",
        "answer": 15,
        "type": "hard",
        "required_op": "MULTIPLICATION",
        "required_symbols": ["*", "×", "x", "(", ")"],
        "instruction": "Get the answer by using MULTIPLICATION (x or ())",
    },
    {
        "display": "20 / 4",
        "answer": 5,
        "type": "hard",
        "required_op": "SUBTRACTION",
        "required_symbols": ["-"],
        "instruction": "Get the answer by using SUBTRACTION",
    },
    {
        "display": "18 / 3",
        "answer": 6,
        "type": "hard",
        "required_op": "SUBTRACTION",
        "required_symbols": ["-"],
        "instruction": "Get the answer by using SUBTRACTION",
    },
    {
        "display": "16 / 2",
        "answer": 8,
        "type": "hard",
        "required_op": "SUBTRACTION",
        "required_symbols": ["-"],
        "instruction": "Get the answer by using SUBTRACTION",
    },
    {
        "display": "24 / 6",
        "answer": 4,
        "type": "hard",
        "required_op": "SUBTRACTION",
        "required_symbols": ["-"],
        "instruction": "Get the answer by using SUBTRACTION",
    },
    {
        "display": "30 / 5",
        "answer": 6,
        "type": "hard",
        "required_op": "ADDITION",
        "required_symbols": ["+"],
        "instruction": "Get the answer by using ADDITION",
    },
    {
        "display": "2^3",
        "answer": 8,
        "type": "hard",
        "required_op": "ADDITION",
        "required_symbols": ["+"],
        "instruction": "Get the answer by using ADDITION",
    },
    {
        "display": "3^2",
        "answer": 9,
        "type": "hard",
        "required_op": "SUBTRACTION",
        "required_symbols": ["-"],
        "instruction": "Get the answer by using SUBTRACTION",
    },
    {
        "display": "4^2",
        "answer": 16,
        "type": "hard",
        "required_op": "MULTIPLICATION",
        "required_symbols": ["*", "×", "x", "(", ")"],
        "instruction": "Get the answer by using MULTIPLICATION (x or ())",
    },
]


def get_random_problem(difficulty="easy", exclude=None):
    """
    Returns a random problem from the pool.

    Parameters:
        difficulty: "easy" for basic algebra/arithmetic,
                    "hard" for alternative operation algebra,
                    "integral" (or "calculus") for calculus integrals.
        exclude: optionally exclude a problem dict so the same
                 problem isn't repeated consecutively.
    """
    if isinstance(difficulty, dict):
        exclude = difficulty
        if "integrand" in exclude:
            difficulty = "integral"
        elif "required_op" in exclude:
            difficulty = "hard"
        else:
            difficulty = "easy"

    diff_str = str(difficulty).lower()
    if diff_str == "hard":
        pool = HARD_PROBLEMS
    elif diff_str in ("integral", "calculus"):
        pool = CHALLENGE_PROBLEMS
    else:
        pool = EASY_PROBLEMS

    available = pool

    if exclude is not None:
        available = [
            p for p in pool
            if p is not exclude
        ]

        if not available:
            available = pool

    return random.choice(available)

