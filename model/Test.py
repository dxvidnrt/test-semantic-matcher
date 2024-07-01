from abc import ABC, abstractmethod
import os
import configparser
from util import json_util, sms_util, graph_representation
import requests
from resolver_modules import service as resolver_service


class TestModel(ABC):
    def __init__(self, name):
        self.path = './'
        self.data_path = os.path.join(self.path, 'data')
        self.config_path = os.path.join(self.path, 'config.ini.default')
        self.data_SMS_path = os.path.join(self.data_path, 'SMS')
        self.data_image_path = os.path.join(self.data_path, 'images')
        self.test_graphs_path = os.path.join(self.data_path, 'test_graphs')
        self.test_path = os.path.join(self.data_path, 'test')
        self.test_json_path = os.path.join(self.test_path, 'test.json')
        self.expected_matches_path = os.path.join(self.test_path, 'expected_matches.json')
        self.retrieved_matches_path = os.path.join(self.test_path, 'retrieved_matches.json')
        self.config = configparser.ConfigParser()
        self.match_request = None
        self.name = name
        self.init()

    def init(self):
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.data_SMS_path, exist_ok=True)
        os.makedirs(self.data_image_path, exist_ok=True)
        os.makedirs(self.test_path, exist_ok=True)
        self.config.read(self.config_path)
        sms_util.clear_all_sms(self.config)
    @abstractmethod
    def create(self):
        """
        Abstract method to create the test scenario.
        """
        pass

    @abstractmethod
    def run(self):
        """
        Abstract method to run the test scenario.
        """
        pass

    def evaluate(self):
        sms_util.get_all_sms(self.config)
        graph_representation.show_graph(self.data_SMS_path, self.data_image_path)
        if not json_util.check_sms(self.data_path): raise AssertionError("SMS are not correct")

        if self.match_request is None:
            print("There is no match request to check.")
        else:
            sms_request = resolver_service.SMSRequest(semantic_id=self.match_request.semantic_id)
            resolver_endpoint = self.config['RESOLVER']['endpoint']
            resolver_port = self.config['RESOLVER']['port']
            response = requests.get(f"{resolver_endpoint}:{resolver_port}/get_semantic_matching_service",
                                    json=sms_request.dict())
            response_json = response.json()
            print(response_json)
            endpoint = response_json['semantic_matching_service_endpoint']
            print(f"Endpoint: {endpoint}")
            sms_util.get_matches_sms(self.match_request, endpoint, self.retrieved_matches_path, self.config)
            if not json_util.check_matches(self.data_path):
                raise AssertionError(f"{self.name} failed")
        print(f"{self.name} worked correctly")
