import os
import subprocess
import datetime
import time
import re
import json
import shutil
import sys


def start_docker_compose(test_dir, log_file):
    """
    Start the docker-compose file in the test directory. Write all logs into log file.
    :param test_dir: Directory where docker-compose file is located
    :param log_file: Path to the log file where output will be saved
    :return: None
    """
    try:
        # Open the log file for appending
        with open(log_file, 'a') as f:
            # Start docker-compose up -d (detached mode)
            subprocess.run(['docker-compose', 'up', '-d'], cwd=test_dir, check=True, stdout=f, stderr=subprocess.STDOUT)

            # Start streaming logs from all containers
            process = subprocess.Popen(['docker-compose', 'logs', '-f'], stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, universal_newlines=True)

            # Write a starting message in the log file
            f.write(f"Started docker-compose up -d at {datetime.datetime.now()}\n")
            f.flush()

            # Continuously stream and write logs to the log file
            while True:
                line = process.stdout.readline().strip()
                if not line:
                    f.write("Break triggered")  # Debugging information
                    f.flush()
                    break
                f.write(line + '\n')
                f.flush()

    # Handle errors in case docker-compose fails
    except subprocess.CalledProcessError as e:
        print(f"Failed to start docker-compose: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure the subprocess is terminated properly
        if 'process' in locals():
            process.terminate()
            process.wait()


def stop_and_cleanup(test_dir, log_file):
    """
    Stop and Remove all services
    :param test_dir: Directory where docker-compose file is located
    :param log_file: Path to the log file where output will be saved
    :return: None
    """
    try:
        with open(log_file, 'a') as f:
            subprocess.run(['docker-compose', 'down', '-v'], check=True, cwd=test_dir, stdout=f,
                           stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop and clean up services in {test_dir}: {e}")


def wait_for_services(test_dir, log_file):
    """
    Run while services are active. Search for container matching pattern 'test-semantic-matcher' and check its status.
    If status is EXITED, stop waiting.
    :param test_dir: Directory where docker-compose file is located
    :param log_file: Path to the log file where output will be saved
    :return: None
    """

    def get_container_exit_code(container_id):
        result = subprocess.run(['docker', 'inspect', '--format', '{{.State.ExitCode}}', container_id],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        res = result.stdout.strip()
        return res

    def get_container_name(container_id):
        try:
            # Run docker inspect to get container details in JSON format
            result = subprocess.run(['docker', 'inspect', '--format', '{{.Name}}', container_id],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            if result.returncode != 0:
                print(f"Error retrieving name for container {container_id}: {result.stderr.strip()}")
                return None

            # Remove any leading '/' character from the container name
            container_name = result.stdout.strip()
            if container_name.startswith('/'):
                container_name = container_name[1:]

            return container_name

        except Exception as e:
            print(f"Exception occurred while retrieving container {container_id} name: {str(e)}")
            return None

    def get_container_state(container_id):
        result = subprocess.run(['docker', 'inspect', container_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        if result.returncode != 0:
            print(f"Error retrieving state for container {container_id}: {result.stderr.strip()}")
            return None

        try:
            container_info = json.loads(result.stdout)
            if not container_info:
                print(f"No information found for container {container_id}")
                return None

            state_info = container_info[0].get('State', {})
            if state_info.get('Running', False):
                return 'RUNNING'
            elif state_info.get('Status') == 'exited':
                return 'EXITED'
            else:
                return state_info.get('Status', 'UNKNOWN')
        except json.JSONDecodeError:
            print(f"Error decoding JSON for container {container_id}")
            return None

    def find_matching_containers(pattern):
        result = subprocess.run(['docker', 'ps', '-a', '--format', '{{.ID}} {{.Names}}'], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, universal_newlines=True)
        containers = result.stdout.strip().split('\n')
        matching_containers = []
        for container in containers:
            container_id, container_name = container.split()
            if re.search(pattern, container_name):
                matching_containers.append(container_id)
        return matching_containers

    pattern = 'test-semantic-matcher'

    with open(log_file, 'a') as f:
        f.write("Starting log...\n")
        f.flush()

        # Start the subprocess to run docker-compose logs -f
        process = subprocess.Popen(['docker-compose', 'logs', '-f'], stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, universal_newlines=True,
                                   cwd=test_dir)

        try:
            running = True
            while running:
                # Read lines from the process output
                line = process.stdout.readline()
                if not line:
                    break
                line = line.strip()
                f.write(line + '\n')  # Write each line to the log file
                f.flush()  # Ensure the line is written immediately

                # Periodically check if the container has exited
                matching_containers = find_matching_containers(pattern)
                if len(matching_containers) != 1:
                    raise AssertionError("There is not exactly one test-semantic-matcher container")
                container_id = matching_containers[0]
                exit_state = get_container_state(container_id)
                if exit_state == "EXITED":
                    exit_code = get_container_exit_code(container_id)
                    output = f"Container {get_container_name(container_id)} exited with code: {exit_code}"
                    # Print success or failure based on exit code
                    if int(exit_code) == 0:
                        print("\033[32m\u2714\033[0m", output)
                    else:
                        print("\033[31m\u2718\033[0m", output)
                    f.write(f"Container {container_id} exited with code: {exit_code}\n")
                    f.flush()
                    running = False
                time.sleep(1)  # Sleep for a while before checking again

        finally:
            # Ensure the process is terminated and wait for it to clean up properly
            process.terminate()
            process.wait()

            f.write("Process terminated\n")
            f.flush()


def generate_docker_compose(test_dir):
    generate_file_path = os.path.join(test_dir, 'generate_docker_compose.py')
    # Check if the generation script exists
    if os.path.isfile(generate_file_path):
        result = subprocess.run(
            [sys.executable, generate_file_path],  # Command to run the script
            cwd=test_dir,  # Change working directory
            capture_output=True,  # Capture standard output and error
            text=True  # Output as text instead of bytes
        )

        if result.returncode != 0:
            print("Script error:\n", result.stderr)


# Main function to coordinate the execution of tests
def main():
    # Set root and log directories
    root_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(root_dir, '../test_cases')
    log_dir = os.path.join(root_dir, '../logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)  # Create log directory if it doesn't exist
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H-%M-%S")
    log_datetime_dir = os.path.join(log_dir, formatted_datetime)
    os.makedirs(log_datetime_dir)

    def start_testcase(cur_tests_dir, cur_test_dir):
        log_path = os.path.join(log_datetime_dir, f'{cur_test_dir}.log')
        data_path = os.path.join(cur_tests_dir, 'data')
        if os.path.isdir(cur_tests_dir) and cur_test_dir.startswith('test_'):
            shutil.rmtree(data_path, ignore_errors=True)
            stop_and_cleanup(cur_tests_dir, log_path)
            generate_docker_compose(cur_tests_dir)
            start_docker_compose(cur_tests_dir, log_path)
            wait_for_services(cur_tests_dir, log_path)
            stop_and_cleanup(cur_tests_dir, log_path)

    for test_dir in sorted(os.listdir(tests_dir)):
        cur_location = os.path.join(tests_dir, test_dir)
        if os.path.isdir(cur_location):
            # Check if directory name starts with 'test_'
            if test_dir.startswith('test_'):
                print(f"Processing test directory: {cur_location}")
                start_testcase(cur_location, test_dir)

            # Check if directory name starts with 'class_'
            elif test_dir.startswith('class_'):
                print(f"Processing class directory: {cur_location}")
                for test_sub_dir in sorted(os.listdir(cur_location)):
                    sub_location = os.path.join(cur_location, test_sub_dir)
                    if os.path.isdir(sub_location):
                        print(f"Processing subdirectory: {sub_location}")
                        start_testcase(sub_location, test_sub_dir)
            else:
                print(f"Error occurred while handling {test_dir}")


if __name__ == "__main__":
    main()
