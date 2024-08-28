from semantic_matcher import model, service_model
from model.Test import TestModel
from util import json_util, graph_util
import random


class Test(TestModel):

    def create(self):
        number_semantic_ids = random.randint(4, 4)

        matches_list = []
        expected_matches = []
        last_match_semantic_id = f'{self.get_random_sms()}/semanticID/0'
        start_server_name = last_match_semantic_id
        for i in range(number_semantic_ids):
            match_semantic_id = f'{self.get_random_sms()}/semanticID/{i + 1}'
            match_i = model.SemanticMatch(
                base_semantic_id=last_match_semantic_id,
                match_semantic_id=match_semantic_id,
                score=round(random.uniform(1.0, 10.0), 1),
                meta_information={'matchSource': "1"}
            )
            matches_list.append(match_i)
            expected_matches = graph_util.find_reachable_matches(start_server_name, matches_list, 0.0)
            last_match_semantic_id = match_semantic_id

        json_util.save_as_json(self.test_json_path, matches_list)
        json_util.save_as_json(self.expected_matches_path, expected_matches)

        self.match_request = service_model.MatchRequest(
            semantic_id=start_server_name,
            score_limit=0.0,
            local_only=False
        )
