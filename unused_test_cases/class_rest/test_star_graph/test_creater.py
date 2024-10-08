from semantic_matcher import service_model, model

from model.Test import TestModel
from util import json_util
import random


class Test(TestModel):

    def create(self):
        number_star_edges = random.randint(100, 200)
        score_limit = random.uniform(0, 1)
        center_server_name = self.get_random_sms()

        matches_list = []
        expected_matches = []

        for i in range(number_star_edges):
            server_name = self.get_random_sms()
            match_i = model.SemanticMatch(
                base_semantic_id=f'{center_server_name}/semanticID/center',
                match_semantic_id=f'{server_name}/semanticID/{i + 1}',
                score=random.uniform(0, 1),
                meta_information={'matchSource': 'Defined by David Niebert'}
            )
            matches_list.append(match_i)
            if match_i.score >= score_limit:
                expected_matches.append(match_i)
        json_util.save_as_json(self.test_json_path, matches_list)
        json_util.save_as_json(self.expected_matches_path, expected_matches)

        self.match_request = service_model.MatchRequest(
            semantic_id=f'{center_server_name}/semanticID/center',
            score_limit=score_limit,
            local_only=False
        )
