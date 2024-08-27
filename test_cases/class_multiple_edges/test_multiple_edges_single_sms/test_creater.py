from semantic_matcher import service_model, model

from model.Test import TestModel
from util import json_util, graph_util
import random


class Test(TestModel):

    def create(self):
        match_1 = model.SemanticMatch(
            base_semantic_id='sms1/semanticID/1',
            match_semantic_id='sms1/semanticID/2',
            score=random.uniform(0.0, 1.0),
            meta_information={'matchSource': '1'}
        )
        match_2 = model.SemanticMatch(
            base_semantic_id='sms1/semanticID/1',
            match_semantic_id='sms1/semanticID/1.1',
            score=1,
            meta_information={'matchSource': '1'}
        )
        match_3 = model.SemanticMatch(
            base_semantic_id='sms1/semanticID/1.1',
            match_semantic_id='sms1/semanticID/2',
            score=random.uniform(0.0, 1.0),
            meta_information={'matchSource': '1'}
        )
        match_4 = model.SemanticMatch(
            base_semantic_id='sms1/semanticID/2',
            match_semantic_id='sms1/semanticID/3',
            score=random.uniform(0.0, 1.0),
            meta_information={'matchSource': '1'}
        )

        matches = [match_1, match_2, match_4, match_3]
        expected_matches = graph_util.find_reachable_matches('sms1/semanticID/1', matches, 0.0)
        json_util.save_as_json(self.test_json_path, matches)
        json_util.save_as_json(self.expected_matches_path, expected_matches)
        self.match_request = service_model.MatchRequest(
            semantic_id='sms1/semanticID/1',
            score_limit=0,
            local_only=False
        )
