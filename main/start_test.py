import sys
import os
import re
import importlib
from model import Test
import subprocess


def main():
    arg1 = sys.argv[1]

    if not re.match(r'^test_', arg1):
        raise ValueError(f"{arg1} does not match the pattern 'test_\\d+'")

    # Construct the module name dynamically
    module_name = "test_creater"

    # Add the directory containing the test case to sys.path
    path_to_test_i = os.path.join('../test_cases', arg1)
    sys.path.insert(0, path_to_test_i)

    # Check if docker-compose can be generated dynamically
    generate_docker_compose_path = os.path.join(path_to_test_i, 'generate_docker_compose.py')
    if os.path.isfile(generate_docker_compose_path):
        try:
            subprocess.run(['python', generate_docker_compose_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

    # Import the module dynamically
    try:
        test_creater = importlib.import_module(module_name, package=path_to_test_i)
    except ModuleNotFoundError:
        raise ImportError(f"Failed to import module '{module_name}'")
    test: Test = test_creater.Test(arg1)
    test.start()


if __name__ == "__main__":
    # sys.argv[0] is the script name itself
    if len(sys.argv) != 2:
        print("Usage: python service.py <arg1>")
        sys.exit(1)
    main()

