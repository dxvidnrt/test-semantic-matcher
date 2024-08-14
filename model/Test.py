from abc import ABC, abstractmethod
import os
import configparser
from util import json_util, sms_util, graph_representation
import requests
from resolver_modules import service as resolver_service
import random


class TestModel(ABC):
    """
    Abstract base class for creating and running test scenarios.
    This class provides a skeleton implementation that includes setting up directories,
    handling configuration, and defining common methods for running and evaluating tests.
    Every concrete test class must inherit from this class and implement the 'create' method.
    """

    def __init__(self, name):
        """
        Initialize the test class by setting up paths, reading configuration, and clearing previous SMS data.

        :param name: The name of the test scenario.
        """
        # Set up basic paths for data, configuration, and test directories.
        self.path = './'
        self.data_path = os.path.join(self.path, 'data')
        self.config_path = os.path.join(self.path, 'config.ini.default')
        self.data_SMS_path = os.path.join(self.data_path, 'SMS')
        self.data_image_path = os.path.join(self.data_path, 'images')
        self.test_graphs_path = os.path.join(self.data_path, 'test_graphs')
        self.test_path = os.path.join(self.data_path, 'test')
        self.test_json_path = os.path.join(self.test_path, 'test.json')
        self.expected_matches_path = os.path.join(self.test_path, 'expected_matches.json')
        self.expected_minimal_matches_path = os.path.join(self.test_path, 'minimal_matches.json')
        self.retrieved_matches_path = os.path.join(self.test_path, 'retrieved_matches.json')

        # Ensure that all necessary directories exist.
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.data_SMS_path, exist_ok=True)
        os.makedirs(self.data_image_path, exist_ok=True)
        os.makedirs(self.test_path, exist_ok=True)

        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        self.match_request = None
        self.name = name

        self.check_sms = True

        # Timeout limit for match retrieval
        self.timeout = 30

        self.sms = None
        if 'ENDPOINTS' in self.config:
            self.sms = [sms for sms, endpoint in self.config["ENDPOINTS"].items()]

        # Clear any existing SMS data using utility methods.
        sms_util.clear_all_sms(self.config)

    @abstractmethod
    def create(self):
        """
        Abstract method to create the test scenario.
        This method should be implemented by subclasses to define their specific test setup.
        """
        raise NotImplementedError("Test cases need to implement this method.")

    def run(self):
        """
        Execute the test case by posting the test JSON data to the appropriate service endpoint.
        """
        sms_util.post_test_case(self.test_json_path, self.config)

    def evaluate(self):
        """
        Retrieving all SMS data and generate graph representation.
        Evaluate results if a match request is given regarding expected matches or minimal matches.

        Raises an assertion error if the expected results are not met.
        """
        if self.check_sms:
            # Retrieve and display SMS data.
            sms_util.get_all_sms(self.config)
            graph_representation.show_graph(self.data_SMS_path, self.data_image_path)
            if not json_util.check_sms(self.data_path):
                raise AssertionError("SMS are not correct")

        if self.match_request is None:
            print("There is no match request to check.")
        else:
            # Evaluate the match request.
            print(f"Evaluating Match Request {self.match_request}")
            sms_request = resolver_service.SMSRequest(semantic_id=self.match_request.semantic_id)
            resolver_endpoint = self.config['RESOLVER']['endpoint']
            resolver_port = self.config['RESOLVER']['port']

            # Send a request to get the semantic matching service endpoint.
            response = requests.get(f"{resolver_endpoint}:{resolver_port}/get_semantic_matching_service",
                                    json=sms_request.dict())
            response_json = response.json()
            endpoint = response_json['semantic_matching_service_endpoint']

            # Get matches for the SMS and check for timeouts.
            if not sms_util.get_matches_sms(self.match_request, endpoint, self.retrieved_matches_path,
                                            self.timeout):
                raise TimeoutError("There was a timeout error requesting matches")

            # Validate the matches and raise an error if they don't match expectations.
            if not json_util.check_matches(self.data_path):
                raise AssertionError(f"{self.name} failed")

        print(f"{self.name} worked correctly")

    def push_endpoints(self):
        """
        Push debug endpoints to the resolver service to overwrite existing endpoints for testing purposes.
        """
        endpoint = self.config['RESOLVER']['endpoint']
        port = self.config['RESOLVER']['port']
        resolver_url = f'{endpoint}:{port}/overwrite_debug_endpoints'
        debug_endpoints = {}

        # Construct the debug endpoints dictionary from the configuration file.
        for key in self.config['ENDPOINTS']:
            debug_endpoints[key] = self.config['ENDPOINTS'][key]

        # Send the debug endpoints to the resolver service.
        debug_endpoints_request = resolver_service.DebugEndpointsRequest(debug_endpoints=debug_endpoints)
        requests.post(resolver_url, json=debug_endpoints_request.dict())

    def start(self):
        """
        Start the test by pushing endpoints, creating the test case, running it, and then evaluating the results.
        """
        self.push_endpoints()
        self.create()
        self.run()
        self.evaluate()

    def get_random_sms(self):
        """
        Get a random SMS endpoint from the list of available SMS endpoints.

        :return: A randomly selected SMS endpoint.
        """
        return random.choice(self.sms)
