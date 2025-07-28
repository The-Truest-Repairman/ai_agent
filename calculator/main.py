import sys
from pkg.calculator import Calculator
from pkg.render import render


def main():
    calculator = Calculator()
    expression = sys.argv[1] if len(sys.argv) > 1 else "2 + 2"
    try:
        result = calculator.evaluate(expression)
        to_print = render(expression, result)
        print(to_print)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()