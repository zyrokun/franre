from __future__ import annotations

from math import comb, gcd


class FranklinReiterError(Exception):
    pass


class NoSolutionError(FranklinReiterError):
    pass


class AmbiguousSolutionError(FranklinReiterError):
    def __init__(self, degree: int):
        self.degree = degree
        super().__init__(f"the polynomial gcd has degree {degree}, not 1")


class NonInvertibleCoefficientError(FranklinReiterError):
    def __init__(self, coefficient: int, modulus: int, factor: int):
        self.coefficient = coefficient
        self.modulus = modulus
        self.factor = factor
        super().__init__(
            f"coefficient {coefficient} is not invertible modulo {modulus}; "
            f"gcd(coefficient, modulus) = {factor}"
        )


Polynomial = list[int]


def _trim(poly: Polynomial, modulus: int) -> Polynomial:
    result = [coefficient % modulus for coefficient in poly]
    while result and result[-1] == 0:
        result.pop()
    return result


def _inverse(value: int, modulus: int) -> int:
    value %= modulus
    factor = gcd(value, modulus)
    if factor != 1:
        raise NonInvertibleCoefficientError(value, modulus, factor)
    return pow(value, -1, modulus)


def _poly_divmod(
    dividend: Polynomial, divisor: Polynomial, modulus: int
) -> tuple[Polynomial, Polynomial]:
    dividend = _trim(dividend, modulus)
    divisor = _trim(divisor, modulus)
    if not divisor:
        raise ZeroDivisionError("polynomial division by zero")
    if not dividend or len(dividend) < len(divisor):
        return [], dividend

    quotient = [0] * max(0, len(dividend) - len(divisor) + 1)
    remainder = dividend[:]
    inverse_lead = _inverse(divisor[-1], modulus)

    while remainder and len(remainder) >= len(divisor):
        shift = len(remainder) - len(divisor)
        factor = remainder[-1] * inverse_lead % modulus
        quotient[shift] = factor
        for index, coefficient in enumerate(divisor):
            remainder[index + shift] = (
                remainder[index + shift] - factor * coefficient
            ) % modulus
        remainder = _trim(remainder, modulus)

    return _trim(quotient, modulus), remainder


def _poly_gcd(first: Polynomial, second: Polynomial, modulus: int) -> Polynomial:
    first = _trim(first, modulus)
    second = _trim(second, modulus)
    while second:
        _, remainder = _poly_divmod(first, second, modulus)
        first, second = second, remainder

    if not first:
        return []
    inverse_lead = _inverse(first[-1], modulus)
    return _trim([coefficient * inverse_lead for coefficient in first], modulus)


def _make_polynomials(
    c1: int, c2: int, modulus: int, exponent: int, a: int, b: int
) -> tuple[Polynomial, Polynomial]:
    first = [(-c1) % modulus] + [0] * (exponent - 1) + [1]

    second = [
        (comb(exponent, degree)
         * pow(a, degree, modulus)
         * pow(b, exponent - degree, modulus))
        % modulus
        for degree in range(exponent + 1)
    ]
    second[0] = (second[0] - c2) % modulus
    return _trim(first, modulus), _trim(second, modulus)


def _check_candidate(
    candidate: int,
    c1: int,
    c2: int,
    modulus: int,
    exponent: int,
    a: int,
    b: int,
) -> int:
    candidate %= modulus
    if pow(candidate, exponent, modulus) != c1 % modulus:
        raise NoSolutionError("candidate does not reproduce the first ciphertext")
    related = (a * candidate + b) % modulus
    if pow(related, exponent, modulus) != c2 % modulus:
        raise NoSolutionError("candidate does not reproduce the second ciphertext")
    return candidate


def _crt_pair(first: int, first_modulus: int, second: int, second_modulus: int) -> int:
    if gcd(first_modulus, second_modulus) != 1:
        raise NoSolutionError("cannot combine non-coprime modulus factors")
    step = (
        (second - first)
        * pow(first_modulus, -1, second_modulus)
    ) % second_modulus
    return (first + first_modulus * step) % (first_modulus * second_modulus)


def _attack_modulus(
    c1: int, c2: int, modulus: int, exponent: int, a: int, b: int
) -> int:
    first_poly, second_poly = _make_polynomials(
        c1, c2, modulus, exponent, a, b
    )

    try:
        common = _poly_gcd(first_poly, second_poly, modulus)
    except NonInvertibleCoefficientError as error:
        factor = error.factor
        other_factor = modulus // factor
        if factor in (1, modulus) or gcd(factor, other_factor) != 1:
            raise

        first_residue = _attack_modulus(
            c1, c2, factor, exponent, a, b
        )
        second_residue = _attack_modulus(
            c1, c2, other_factor, exponent, a, b
        )
        candidate = _crt_pair(
            first_residue, factor, second_residue, other_factor
        )
        return _check_candidate(candidate, c1, c2, modulus, exponent, a, b)

    if len(common) == 1:
        raise NoSolutionError("the ciphertext polynomials have no common root")
    degree = len(common) - 1
    if degree != 1:
        raise AmbiguousSolutionError(degree)

    candidate = -common[0] * _inverse(common[1], modulus) % modulus
    return _check_candidate(candidate, c1, c2, modulus, exponent, a, b)


def _execute(
    c1: int,
    c2: int,
    n: int,
    e: int,
    *,
    a: int,
    b: int,
) -> int:
    if not isinstance(n, int) or isinstance(n, bool) or n <= 1:
        raise ValueError("n must be an integer greater than 1")
    if not isinstance(e, int) or isinstance(e, bool) or e < 2:
        raise ValueError("e must be an integer greater than or equal to 2")
    if not all(isinstance(value, int) and not isinstance(value, bool)
               for value in (c1, c2, a, b)):
        raise TypeError("c1, c2, a, and b must be integers")

    return _attack_modulus(c1, c2, n, e, a % n, b % n)


def solve(
    c1: int,
    c2: int,
    n: int,
    e: int,
    *,
    a: int,
    b: int,
) -> None:
    try:
        message = _execute(c1, c2, n, e, a=a, b=b)
    except (FranklinReiterError, TypeError, ValueError):
        print("no solutions lol")
        return

    print(f"woah, its m : {message}")
