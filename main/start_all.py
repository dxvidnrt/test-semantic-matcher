import os
import subprocess
import datetime


def install_requirements(test_dir):
    requirements_path = os.path.join(test_dir, 'requirements.txt')
    if os.path.exists(requirements_path):
        try:
            print(f"Installing requirements in {test_dir}")
            subprocess.run(['pip', 'install', '-r', requirements_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install requirements in {test_dir}: {e}")


def start_docker_compose(test_dir, log_file):
    try:
        with open(log_file, 'w') as f:
            subprocess.run(
                ['docker-compose', 'up', '-d'],
                check=True,
                cwd=test_dir,
                stdout=f,
                stderr=subprocess.STDOUT  # Merge stderr with stdout
            )
    except subprocess.CalledProcessError as e:
        print(f"Failed to start services in {test_dir}: {e}")


def clone_repos():
    repos = {
        "semantic_id_resolver": "https://github.com/dxvidnrt/semantic_id_resolver",
        "python-semantic-matcher": "https://github.com/dxvidnrt/python-semantic-matcher"
    }
    for name, url in repos.items():
        target_dir = f"../../../{name}"
        if not os.path.exists(target_dir):
            subprocess.run(['git', 'clone', url, target_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def wait_for_services(test_dir, log_file):
    try:
        with open(log_file, 'w') as f:
            # Run docker-compose logs -f to continuously stream logs
            process = subprocess.Popen(['docker-compose', 'logs', '-f'], stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       cwd=test_dir)

            # Monitor the output for the container named 'semantic_matcher'
            for line in iter(process.stdout.readline, b''):
                line = line.decode('utf-8').strip()
                f.write(line + '\n')  # Write line to log file

                # Check if the line indicates the container has exited
                if f"exited with code " in line:
                    # Extract the exit code from the log line
                    exit_code = line.split('exited with code ')[1]
                    print(f"Container semantic_matcher exited with code: {exit_code}")
                    break  # Exit the loop once we find the exit code

    except subprocess.CalledProcessError as e:
        print(f"Failed while waiting for services in {test_dir}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def stop_and_cleanup(test_dir, log_file):
    try:
        with open(log_file, 'w') as f:
            subprocess.run(['docker-compose', 'down', '-v'], check=True, cwd=test_dir, stdout=f,
                           stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop and clean up services in {test_dir}: {e}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(base_dir)
    tests_dir = os.path.join(root_dir, 'test_cases')
    log_dir = os.path.join(root_dir, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H-%M-%S")
    log_datetime_dir = os.path.join(log_dir, formatted_datetime)
    os.makedirs(log_datetime_dir)
    clone_repos()

    for test_dir in sorted(os.listdir(tests_dir)):
        full_test_dir = os.path.join(tests_dir, test_dir)
        log_path = os.path.join(log_datetime_dir, f'{test_dir}.log')
        if os.path.isdir(full_test_dir) and test_dir.startswith('test_'):
            start_docker_compose(full_test_dir, log_path)
            wait_for_services(full_test_dir, log_path)
            stop_and_cleanup(full_test_dir, log_path)
            print(f"Finished Iteration {test_dir}")


if __name__ == "__main__":
    main()
