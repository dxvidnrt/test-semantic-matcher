from semantic_matcher import service_model, model
from model.Test import TestModel
from util import json_util


class Test(TestModel):
    def create(self):
        match_sms_1 = model.SemanticMatch(
            base_semantic_id='sms1/semanticID/1',
            match_semantic_id='sms1/semanticID/2',
            score=0.9,
            meta_information={'matchSource': '1'}
        )
        match_sms_2 = model.SemanticMatch(
            base_semantic_id='sms1/semanticID/2',
            match_semantic_id='sms1/semanticID/3',
            score=0.9,
            meta_information={'matchSource': '1'}
        )
        match_sms_3 = model.SemanticMatch(
            base_semantic_id='sms1/semanticID/3',
            match_semantic_id='sms1/semanticID/1',
            score=0.9,
            meta_information={'matchSource': '1'}
        )
        matches_list = [match_sms_1, match_sms_2, match_sms_3]
        json_util.save_as_json(self.test_json_path, matches_list)
        json_util.save_as_json(self.expected_minimal_matches_path, [match_sms_2])
        self.match_request = service_model.MatchRequest(
            semantic_id='sms1/semanticID/1',
            score_limit=0.3,
            local_only=True
        )
