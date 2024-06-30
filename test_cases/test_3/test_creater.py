from semantic_matcher import model, service_model
from model.Test import TestModel
from util import sms_util, graph_representation, json_util


class Test(TestModel):
    def create(self):
        match_1 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/semanticID/Dog',
            match_semantic_id='s-heppner.com/semanticID/Cat',
            score=0.7,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        match_2 = model.SemanticMatch(
            base_semantic_id='s-heppner.com/semanticID/Cat',
            match_semantic_id='s-heppner.com/semanticID/Cat_2',
            score=0.9,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        match_3 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/semanticID/Dog',
            match_semantic_id='s-heppner.com/semanticID/Fish',
            score=0.3,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        matches_list = [match_1, match_2, match_3]
        json_util.save_as_json(self.test_json_path, matches_list)

        expected_matches = [match_1, match_2]
        json_util.save_as_json(self.expected_matches_path, expected_matches)

    def run(self):
        sms_util.post_test_case(self.test_json_path, self.config)
        match_request = service_model.MatchRequest(
            semantic_id='dxvidnrt.com/semanticID/Dog',
            score_limit=0.49,
            local_only=False
        )
        endpoint = self.config['ENDPOINTS']['sms2']
        sms_util.get_matches_sms(match_request, endpoint, self.retrieved_matches_path, self.config)

    def evaluate(self):
        sms_util.get_all_sms(self.config)
        graph_representation.show_graph(self.data_SMS_path, self.data_image_path)
        if json_util.check_sms(self.data_path) and json_util.check_matches(self.data_path):
            print("Test_3 worked correctly")
        else:
            raise AssertionError("Test_3 failed")
