from semantic_matcher import service_model, model
import json

from model.Test import TestModel
from util import sms_util, graph_representation, json_util


class Test(TestModel):
    def create(self):
        matches_list = []
        # TODO Load random SMS and add dynamically
        n = 5
        for i in range(n):
            match_i = model.SemanticMatch(
                base_semantic_id='dxvidnrt.com/semanticID/center',
                match_semantic_id=f'dxvidnrt.com/semanticID/{i+1}',
                score=1,
                meta_information={'matchSource': 'Defined by David Niebert'}
            )
            matches_list.append(match_i)
        json_util.save_as_json(self.test_json_path, matches_list)

    def run(self):
        sms_util.post_test_case(self.test_json_path, self.config)

    def evaluate(self):
        sms_util.get_all_sms(self.config)
        graph_representation.show_graph(self.data_SMS_path, self.data_image_path)
        if json_util.check_test(self.data_path):
            print("Test_star worked correctly") # TODO get name dynamically
        else:
            raise AssertionError("Test_star failed")
