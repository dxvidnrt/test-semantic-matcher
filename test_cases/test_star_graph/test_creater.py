from semantic_matcher import service_model, model

from model.Test import TestModel
from util import sms_util, graph_representation, json_util
import random


class Test(TestModel):
    def __init__(self):
        self.number_star_edges = random.randint(1, 10)
        self.score_limit = random.uniform(0, 1)
        self.server_names = ["dxvidnrt.com", "s-heppner.com"]  # TODO get from config/resolver
        self.center_server_name = random.choice(self.server_names)

    def create(self):
        matches_list = []
        expected_matches = []

        # TODO Add function to get all adress name from id_resolver. Or load addresses into id:resolver from config.
        for i in range(self.number_star_edges):
            server_name = random.choice(self.server_names)
            match_i = model.SemanticMatch(
                base_semantic_id=f'{self.center_server_name}.com/semanticID/center',
                match_semantic_id=f'{server_name}/semanticID/{i+1}',
                score=random.uniform(0, 1),
                meta_information={'matchSource': 'Defined by David Niebert'}
            )
            matches_list.append(match_i)
            if match_i.score >= self.score_limit:
                expected_matches.append(match_i)
        json_util.save_as_json(self.test_json_path, matches_list)
        json_util.save_as_json(self.expected_matches_path, expected_matches)

    def run(self):
        sms_util.post_test_case(self.test_json_path, self.config)
        match_request = service_model.MatchRequest(
            semantic_id=f'{self.center_server_name}/semanticID/center',
            score_limit=self.score_limit,
            local_only=False
        )
        endpoint = self.config['ENDPOINTS']['sms2']
        sms_util.get_matches_sms(match_request, endpoint, self.retrieved_matches_path, self.config)

    def evaluate(self):  # TODO put into abstract class and check in json_util if files exist
        sms_util.get_all_sms(self.config)
        graph_representation.show_graph(self.data_SMS_path, self.data_image_path)
        if json_util.check_sms(self.data_path) and json_util.check_matches(self.data_path):
            print("Test_star worked correctly") # TODO get name dynamically
        else:
            raise AssertionError("Test_star failed")
