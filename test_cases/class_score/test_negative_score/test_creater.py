from semantic_matcher import model, service_model
from model.Test import TestModel
from util import json_util


class Test(TestModel):
    def create(self):
        match_1 = model.SemanticMatch(
            base_semantic_id='sms1/semanticID/1',
            match_semantic_id='sms2/semanticID/2',
            score=-0.7,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        match_2 = model.SemanticMatch(
            base_semantic_id='sms2/semanticID/2',
            match_semantic_id='sms2/semanticID/2.2',
            score=0.9,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        match_3 = model.SemanticMatch(
            base_semantic_id='sms1/semanticID/1',
            match_semantic_id='sms2/semanticID/3',
            score=0.3,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        matches_list = [match_1, match_2, match_3]
        json_util.save_as_json(self.test_json_path, matches_list)

        expected_matches = [match_1, match_2, match_3]
        json_util.save_as_json(self.expected_matches_path, expected_matches)

        self.match_request = service_model.MatchRequest(
            semantic_id='sms1/semanticID/1',
            score_limit=-1000.,
            local_only=False
        )
