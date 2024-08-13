import random
import yaml
import configparser

# Define the base structure of the Docker Compose file
docker_compose_template = {
    'version': '3.8',
    'services': {},
    'networks': {
        'semantic_network': {
            'driver': 'bridge'
        }
    }
}

# Generate a random number of services (between 1 and 5 for example)
num_services = random.randint(2, 3)
services = []

# Create services dynamically
for i in range(num_services):
    image = "local/python-semantic-matcher"
    service_name = f'python-semantic-matcher_{i + 1}'
    context = "https://github.com/dxvidnrt/python-semantic-matcher.git"
    port_host = 8000 + i
    port_container = 8010 + i
    services.append(f"http://{service_name}:8000")

    docker_compose_template['services'][service_name] = {
        'image': image,
        'build': {
            'context': context
        },
        'ports': [
            f"{port_host}:{port_container}"  # Example port mapping
        ],
        'networks': [
            'semantic_network'
        ],
        'healthcheck': {
            'test': f"CMD curl -f http://{service_name}:8000",  # Adjust here for your specific format
            'interval': '10s',
            'timeout': '5s',
            'retries': 5
        }
    }

# Add semantic_id_resolver service
docker_compose_template['services']['semantic_id_resolver'] = {
    'image': 'local/semantic_id_resolver',
    'build': {
        'context': 'https://github.com/dxvidnrt/semantic_id_resolver.git'
    },
    'ports': [
        '8125:8015'
    ],
    'networks': [
        'semantic_network'
    ],
    'depends_on': [f'python-semantic-matcher_{i+1}' for i in range(num_services)]
}

# Add test-semantic-matcher service
docker_compose_template['services']['test-semantic-matcher'] = {
    'build': {
        'context': '.'
    },
    'ports': [
        '8100:8019'
    ],
    'networks': [
        'semantic_network'
    ],
    'volumes': [
        './data:/app/data',
        '../../../main:/app/main',
        '../../../util:/app/util',
        '../../../model:/app/model'
    ],
    'depends_on': [f'python-semantic-matcher_{i+1}' for i in range(num_services)]
}

# Save the generated Docker Compose YAML to a file
with open('docker-compose.yml', 'w') as f:
    yaml.dump(docker_compose_template, f, default_flow_style=False)

config_file = './config.ini.default'
config = configparser.ConfigParser()
config.read(config_file)
for key in config['ENDPOINTS']:
    config.remove_option('ENDPOINTS', key)
for i in range(len(services)):
    config.set('ENDPOINTS', f'sms{i+1}', services[i])
with open('config.ini.default', 'w') as f:
    config.write(f)


print(f"Generated Docker Compose file with {num_services} services and semantic_id_resolver.")
