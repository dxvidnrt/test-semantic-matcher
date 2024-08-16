from semantic_matcher import service_model, model

from model.Test import TestModel
from util import json_util, graph_util
import random


class Test(TestModel):

    def __init__(self, name):
        super().__init__(name)
        self.start_server_name = None

    def create(self):

        matches_list = []

        semantic_ids_list = []
        semantic_id_counter = 0
        while semantic_id_counter <= random.randint(8, 12):
            for sms in self.sms:
                number_semantic_ids = random.randint(0, 6)
                for _ in range(number_semantic_ids):
                    semantic_id_counter += 1
                    semantic_id = f'{sms}/semanticID/{semantic_id_counter}'
                    semantic_ids_list.append(semantic_id)

        number_matches = semantic_id_counter
        start_semantic_id = None
        while len(matches_list) < number_matches:
            two_matches = random.sample(semantic_ids_list, 2)
            if start_semantic_id is None:
                start_semantic_id = two_matches[0]
            match = model.SemanticMatch(
                base_semantic_id=two_matches[0],
                match_semantic_id=two_matches[1],
                score=random.uniform(0.8, 0.9),
                meta_information={'matchSource': 'Simple Source'}
            )
            matches_list.append(match)

        score_limit = random.uniform(0.7, 0.8)

        expected_matches = graph_util.find_reachable_matches(start_semantic_id, matches_list, score_limit)

        json_util.save_as_json(self.test_json_path, matches_list)
        json_util.save_as_json(self.expected_matches_path, expected_matches)

        if start_semantic_id is not None:
            self.match_request = service_model.MatchRequest(
                semantic_id=start_semantic_id,
                score_limit=score_limit,
                local_only=False
            )
