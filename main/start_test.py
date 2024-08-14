import sys
import re
import importlib
from model import Test


def main():
    """
    Main function that validates the argument, dynamically imports a module,
    creates a Test instance, and starts the test.
    """
    test_name = sys.argv[1]

    if not re.match(r'^test_', test_name):
        raise ValueError(f"{test_name} does not match the pattern 'test_\\d+'")

    # Construct the module name dynamically
    module_name = "test_creater"

    # Import the module dynamically
    try:
        test_creater = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        raise ImportError(f"Failed to import module '{module_name}'") from e

    try:
        test: Test = test_creater.Test(test_name)
    except AttributeError as e:
        raise ImportError(f"Module '{module_name}' does not have a class named 'Test'") from e

    test.start()


if __name__ == "__main__":
    # sys.argv[0] is the script name itself
    if len(sys.argv) != 2:
        print("Usage: python service.py <arg1>")
        sys.exit(1)
    main()

