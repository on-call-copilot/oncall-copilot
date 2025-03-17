from operations import add, subtract, multiply, divide
from utils import parse_args

if __name__ == "__main__":
    # For simplicity, let's just take two arguments and an operation from the command line
    args = parse_args()
    a = args.a
    b = args.b
    op = args.op

    if op == "add":
        result = add(a, b)
    elif op == "subtract":
        result = subtract(a, b)
    elif op == "multiply":
        result = multiply(a, b)
    elif op == "divide":
        # Handle division by zero gracefully
        try:
            result = divide(a, b)
        except ZeroDivisionError:
            result = "Error: Division by zero!"
    else:
        result = f"Unknown operation: {op}"

    print(f"Result: {result}")

