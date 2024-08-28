from semantic_matcher import model, service_model
from model.Test import TestModel
from util import json_util
import random


class Test(TestModel):
    def create(self):
        match_sms_1 = model.SemanticMatch(
            base_semantic_id='sms1/semanticID/1',
            match_semantic_id='sms2/semanticID/2',
            score=round(random.uniform(0.5, 0.99), 1),
            meta_information={'matchSource': '1'}
        )
        match_sms_2 = model.SemanticMatch(
            base_semantic_id='sms2/semanticID/2',
            match_semantic_id='sms3/semanticID/3',
            score=round(random.uniform(0.5, 0.99), 1),
            meta_information={'matchSource': '1'}
        )
        match_sms_3 = model.SemanticMatch(
            base_semantic_id='sms3/semanticID/3',
            match_semantic_id='sms1/semanticID/1',
            score=round(random.uniform(0.5, 0.99), 1),
            meta_information={'matchSource': '1'}
        )
        matches_list = [match_sms_1, match_sms_2, match_sms_3]
        json_util.save_as_json(self.test_json_path, matches_list)
        json_util.save_as_json(self.expected_minimal_matches_path, [match_sms_2])
        self.match_request = service_model.MatchRequest(
            semantic_id='sms1/semanticID/1',
            score_limit=random.uniform(0.1, 0.15),
            local_only=False
        )
