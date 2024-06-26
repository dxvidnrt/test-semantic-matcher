from abc import ABC, abstractmethod
import os
import configparser
from util import sms_util


class TestModel(ABC):
    def __init__(self):
        self.path = './'
        self.data_path = os.path.join(self.path, 'data')
        self.config_path = os.path.join(self.path, 'config.ini.default')
        self.data_SMS_path = os.path.join(self.data_path, 'SMS')
        self.data_image_path = os.path.join(self.data_path, 'images')
        self.test_graphs_path = os.path.join(self.data_path, 'test_graphs')
        self.test_path = os.path.join(self.data_path, 'test.json')
        self.config = configparser.ConfigParser()
        self.init()

    def init(self):
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.data_SMS_path, exist_ok=True)
        os.makedirs(self.data_image_path, exist_ok=True)
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

    @abstractmethod
    def evaluate(self):
        """
        Abstract method to evaluate the test results.
        """
        pass
