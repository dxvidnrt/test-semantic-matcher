#ChatGPT code:
import os
import subprocess


def install_requirements(test_dir):
    requirements_path = os.path.join(test_dir, 'requirements.txt')
    if os.path.exists(requirements_path):
        try:
            print(f"Installing requirements in {test_dir}")
            subprocess.run(['pip', 'install', '-r', requirements_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install requirements in {test_dir}: {e}")


def start_docker_compose(test_dir):
    try:
        print(f"Starting services in {test_dir}")
        subprocess.run(['docker-compose', 'up', '-d'], check=True, cwd=test_dir)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start services in {test_dir}: {e}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(base_dir, 'test_cases')

    for test_dir in sorted(os.listdir(tests_dir)):
        full_test_dir = os.path.join(tests_dir, test_dir)
        if os.path.isdir(full_test_dir) and test_dir.startswith('test_'):
            install_requirements(full_test_dir)
            start_docker_compose(full_test_dir)

    print("All services started.")


if __name__ == "__main__":
    main()
