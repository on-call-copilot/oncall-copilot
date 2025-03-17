import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="A simple command-line calculator.")
    parser.add_argument("--a", type=float, required=True, help="First number")
    parser.add_argument("--b", type=float, required=True, help="Second number")
    parser.add_argument("--op", type=str, required=True, choices=["add", "subtract", "multiply", "divide"], help="Operation to perform")
    return parser.parse_args()

