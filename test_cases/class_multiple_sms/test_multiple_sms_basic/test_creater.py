from semantic_matcher import model, service_model
from model.Test import TestModel
from util import json_util


class Test(TestModel):
    def create(self):
        match_1 = model.SemanticMatch(
            base_semantic_id='sms1/SemanticID/1',
            match_semantic_id='sms2/SemanticID/2',
            score=1,
            meta_information={'matchSource': '1'}
        )
        match_2 = model.SemanticMatch(
            base_semantic_id='sms2/SemanticID/2',
            match_semantic_id='sms2/SemanticID/3',
            score=1,
            meta_information={'matchSource': '1'}
        )
        json_util.save_as_json(self.test_json_path, [match_1, match_2])
        json_util.save_as_json(self.expected_minimal_matches_path, [match_2])

        self.match_request = service_model.MatchRequest(
            semantic_id='sms1/SemanticID/1',
            score_limit=0,
            local_only=False
        )
