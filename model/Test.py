import shutil
from abc import ABC, abstractmethod
import os
import configparser
from util import json_util, sms_util, graph_representation
import requests
from resolver_modules import service as resolver_service
import random


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
        self.expected_minimal_matches_path = os.path.join(self.test_path, 'minimal_matches.json')
        self.retrieved_matches_path = os.path.join(self.test_path, 'retrieved_matches.json')

        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.data_SMS_path, exist_ok=True)
        os.makedirs(self.data_image_path, exist_ok=True)
        os.makedirs(self.test_path, exist_ok=True)

        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        self.match_request = None
        self.name = name

        self.sms = None
        if 'ENDPOINTS' in self.config:
            self.sms = [sms for sms, endpoint in self.config["ENDPOINTS"].items()]

        sms_util.clear_all_sms(self.config)


    @abstractmethod
    def create(self):
        """
        Abstract method to create the test scenario.
        """
        pass

    def run(self):
        sms_util.post_test_case(self.test_json_path, self.config)

    def evaluate(self):
        sms_util.get_all_sms(self.config)
        graph_representation.show_graph(self.data_SMS_path, self.data_image_path)
        if not json_util.check_sms(self.data_path):
            raise AssertionError("SMS are not correct")

        if self.match_request is None:
            print("There is no match request to check.")
        else:
            sms_request = resolver_service.SMSRequest(semantic_id=self.match_request.semantic_id)
            resolver_endpoint = self.config['RESOLVER']['endpoint']
            resolver_port = self.config['RESOLVER']['port']
            response = requests.get(f"{resolver_endpoint}:{resolver_port}/get_semantic_matching_service",
                                    json=sms_request.dict())
            response_json = response.json()
            endpoint = response_json['semantic_matching_service_endpoint']
            sms_util.get_matches_sms(self.match_request, endpoint, self.retrieved_matches_path, self.config)
            if not json_util.check_matches(self.data_path):
                raise AssertionError(f"{self.name} failed")
        print(f"{self.name} worked correctly")

    def push_endpoints(self):
        endpoint = self.config['RESOLVER']['endpoint']
        port = self.config['RESOLVER']['port']
        resolver_url = f'{endpoint}:{port}/overwrite_debug_endpoints'
        debug_endpoints = {}
        for key in self.config['ENDPOINTS']:
            debug_endpoints[key] = self.config['ENDPOINTS'][key]
        debug_endpoints_request = resolver_service.DebugEndpointsRequest(debug_endpoints=debug_endpoints)
        requests.post(resolver_url, json=debug_endpoints_request.dict())

    def start(self):
        self.push_endpoints()
        self.create()
        self.run()
        self.evaluate()

    def get_random_sms(self):
        return random.choice(self.sms)
