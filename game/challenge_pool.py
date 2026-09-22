import random


CHALLENGE_PROBLEMS = [
    {
        "integrand": "3",
        "lower_bound": 1,
        "upper_bound": 4,
        "answer": 9,
        "display": "integral 1->4 of 3 dx",
    },
    {
        "integrand": "2x",
        "lower_bound": 1,
        "upper_bound": 3,
        "answer": 8,
        "display": "integral 1->3 of 2x dx",
    },
    {
        "integrand": "x^2",
        "lower_bound": 0,
        "upper_bound": 3,
        "answer": 9,
        "display": "integral 0->3 of x^2 dx",
    },
    {
        "integrand": "4x",
        "lower_bound": 0,
        "upper_bound": 5,
        "answer": 50,
        "display": "integral 0->5 of 4x dx",
    },
    {
        "integrand": "x^2+1",
        "lower_bound": 0,
        "upper_bound": 3,
        "answer": 12,
        "display": "integral 0->3 of (x^2+1) dx",
    },
    {
        "integrand": "6x^2",
        "lower_bound": 1,
        "upper_bound": 2,
        "answer": 14,
        "display": "integral 1->2 of 6x^2 dx",
    },
    {
        "integrand": "3x^2+2x",
        "lower_bound": 0,
        "upper_bound": 2,
        "answer": 12,
        "display": "integral 0->2 of (3x^2+2x) dx",
    },
    {
        "integrand": "x^3",
        "lower_bound": 0,
        "upper_bound": 2,
        "answer": 4,
        "display": "integral 0->2 of x^3 dx",
    },
    {
        "integrand": "5",
        "lower_bound": 2,
        "upper_bound": 8,
        "answer": 30,
        "display": "integral 2->8 of 5 dx",
    },
    {
        "integrand": "2x+3",
        "lower_bound": 1,
        "upper_bound": 5,
        "answer": 36,
        "display": "integral 1->5 of (2x+3) dx",
    },
]


def get_random_problem(exclude=None):
    """
    Returns a random problem from the pool.

    Optionally excludes a problem dict so the
    same problem isn't repeated consecutively.
    """

    available = CHALLENGE_PROBLEMS

    if exclude is not None:
        available = [
            p for p in CHALLENGE_PROBLEMS
            if p is not exclude
        ]

        if not available:
            available = CHALLENGE_PROBLEMS

    return random.choice(available)
