from semantic_matcher import service_model, model
import json

from model.Test import TestModel
from util import sms_util, graph_representation, json_util

config_path = './config.ini.default'  # Use relative path within Docker container
data_path = './data'


class Test(TestModel):
    def create(self):
        match_sms_1 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/semanticID/1',
            match_semantic_id='dxvidnrt.com/semanticID/1',
            score=1,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        matches_list = [match_sms_1]
        json_util.save_as_json(self.test_json_path, matches_list)

    def run(self):
        sms_util.post_test_case(self.test_json_path, self.config)
