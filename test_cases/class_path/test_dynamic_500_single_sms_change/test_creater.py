from semantic_matcher import service_model, model

from model.Test import TestModel
from util import json_util
import random


class Test(TestModel):

    def create(self):
        number_semantic_ids = random.randint(400, 600)

        matches_list = []
        minimal_matches = []
        cur_sms = 'sms1'
        cur_match_source = "1"
        last_match_semantic_id = f'{cur_sms}/semanticID/0'
        for i in range(number_semantic_ids):
            match_semantic_id = f'{cur_sms}/semanticID/{i+1}'
            match_i = model.SemanticMatch(
                base_semantic_id=last_match_semantic_id,
                match_semantic_id=match_semantic_id,
                score=1,
                meta_information={'matchSource': f"{cur_match_source}"}
            )
            matches_list.append(match_i)
            if i == number_semantic_ids // 2:
                cur_sms = 'sms2'
                cur_match_source = '2'

            if i == number_semantic_ids - 1:
                minimal_matches.append(match_i)
            last_match_semantic_id = match_semantic_id

        json_util.save_as_json(self.test_json_path, matches_list)
        json_util.save_as_json(self.expected_minimal_matches_path, minimal_matches)

        self.match_request = service_model.MatchRequest(
            semantic_id='sms1/semanticID/0',
            score_limit=0,
            local_only=False
        )

        self.check_sms = False
