from semantic_matcher import model, service_model
from model.Test import TestModel
from util import json_util
import random


class Test(TestModel):

    def create(self):
        number_nodes = random.randint(15, 20)
        number_matches = random.randint(int((1 / 6) * (number_nodes ** 2)), int((1 / 3) * (number_nodes ** 2)))
        base_semantic_ids = [f"{self.get_random_sms()}/SemanticId/{i}" for i in range(number_nodes)]
        matches = []
        for i in range(number_matches):
            match_i = model.SemanticMatch(
                base_semantic_id=random.choice(base_semantic_ids),
                match_semantic_id=random.choice(base_semantic_ids),
                score=random.uniform(0.000001, 1.0),
                meta_information={'matchSource': 'Defined by David Niebert'}
            )
            matches.append(match_i)

        minimal_matches = []

        length_path = random.randint(5, number_nodes)
        start_server_name = random.choice(base_semantic_ids)
        last_match_id = start_server_name
        cur_score = 1
        cut_off_score = random.uniform(0.01, 0.2)
        for i in range(length_path):
            match_semantic_id = random.choice(base_semantic_ids)
            score = random.uniform(0.8, 1.0)
            match_i = model.SemanticMatch(
                base_semantic_id=last_match_id,
                match_semantic_id=match_semantic_id,
                score=score,
                meta_information={'matchSource': 'Defined by David Niebert'}
            )
            matches.append(match_i)
            cur_score *= score
            if cur_score >= cut_off_score:
                minimal_matches.append(match_i)
            last_match_id = match_semantic_id

        json_util.save_as_json(self.test_json_path, matches)
        json_util.save_as_json(self.expected_minimal_matches_path, minimal_matches)

        self.match_request = service_model.MatchRequest(
            semantic_id=start_server_name,
            score_limit=cut_off_score,
            local_only=False
        )
