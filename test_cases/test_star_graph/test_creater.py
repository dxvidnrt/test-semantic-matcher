import requests
from semantic_matcher import service_model, model
from resolver_modules import service as resolver_service

from model.Test import TestModel
from util import sms_util, graph_representation, json_util
import random


class Test(TestModel):
    def __init__(self, name):
        super().__init__(name)
        self.number_star_edges = random.randint(1, 10)
        self.score_limit = random.uniform(0, 1)
        self.server_names = ["dxvidnrt.com", "s-heppner.com"]  # TODO get from config/resolver
        self.center_server_name = random.choice(self.server_names)
        self.match_request: service_model.MatchRequest = None

    def create(self):
        matches_list = []
        expected_matches = []

        # TODO Add function to get all adress name from id_resolver. Or load addresses into id:resolver from config.
        for i in range(self.number_star_edges):
            server_name = random.choice(self.server_names)
            match_i = model.SemanticMatch(
                base_semantic_id=f'{self.center_server_name}/semanticID/center',
                match_semantic_id=f'{server_name}/semanticID/{i + 1}',
                score=random.uniform(0, 1),
                meta_information={'matchSource': 'Defined by David Niebert'}
            )
            matches_list.append(match_i)
            if match_i.score >= self.score_limit:
                expected_matches.append(match_i)
        json_util.save_as_json(self.test_json_path, matches_list)
        json_util.save_as_json(self.expected_matches_path, expected_matches)
        print(f"Cut-off score: {self.score_limit}")

    def run(self):
        sms_util.post_test_case(self.test_json_path, self.config)
        self.match_request = service_model.MatchRequest(
            semantic_id=f'{self.center_server_name}/semanticID/center',
            score_limit=self.score_limit,
            local_only=False
        )

