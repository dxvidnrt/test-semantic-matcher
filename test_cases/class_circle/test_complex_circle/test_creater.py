from semantic_matcher import service_model, model
from model.Test import TestModel
from util import json_util, graph_util
import random


class Test(TestModel):
    def create(self):
        number_semantic_ids = random.randint(8, 12)

        matches_list = []
        last_match_semantic_id = 'sms1/semanticID/1'
        start_semantic_id = last_match_semantic_id
        semantic_ids = []
        for i in range(number_semantic_ids):
            match_semantic_id = f'{self.get_random_sms()}/semanticID/{i + 2}'
            semantic_ids.append(match_semantic_id)
            match_i = model.SemanticMatch(
                base_semantic_id=last_match_semantic_id,
                match_semantic_id=match_semantic_id,
                score=1,
                meta_information={'matchSource': "Simple Source"}
            )
            last_match_semantic_id = match_semantic_id
            matches_list.append(match_i)
            if i == number_semantic_ids - 1:
                match = model.SemanticMatch(
                    base_semantic_id=match_semantic_id,
                    match_semantic_id=start_semantic_id,
                    score=1,
                    meta_information={'matchSource': "1"}
                )
                matches_list.append(match)

        number_random_matches = number_semantic_ids // 2
        for _ in range(number_random_matches):
            base_semantic_id, match_semantic_id = random.sample(semantic_ids, 2)
            random_match = model.SemanticMatch(
                base_semantic_id=base_semantic_id,
                match_semantic_id=match_semantic_id,
                score=1,
                meta_information={'matchSource': "2"}
            )
            matches_list.append(random_match)

        expected_matches = graph_util.find_reachable_matches(start_semantic_id, matches_list, 1.0)
        json_util.save_as_json(self.test_json_path, matches_list)
        json_util.save_as_json(self.expected_matches_path, expected_matches)

        self.match_request = service_model.MatchRequest(
            semantic_id=start_semantic_id,
            score_limit=0.0,
            local_only=True
        )
