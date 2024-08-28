import random

from semantic_matcher import model, service_model
from model.Test import TestModel
from util import json_util, graph_util


class Test(TestModel):
    def create(self):
        match_1 = model.SemanticMatch(
            base_semantic_id='sms1/SemanticID/1',
            match_semantic_id='sms2/SemanticID/2',
            score=round(random.uniform(0.1, 0.9), 1),
            meta_information={'matchSource': '1'}
        )
        match_2 = model.SemanticMatch(
            base_semantic_id='sms2/SemanticID/2',
            match_semantic_id='sms3/SemanticID/3',
            score=round(random.uniform(0.1, 0.9), 1),
            meta_information={'matchSource': '1'}
        )
        match_3 = model.SemanticMatch(
            base_semantic_id='sms3/SemanticID/3',
            match_semantic_id='sms4/SemanticID/4',
            score=round(random.uniform(0.1, 0.9), 1),
            meta_information={'matchSource': '1'}
        )
        match_4 = model.SemanticMatch(
            base_semantic_id='sms4/SemanticID/4',
            match_semantic_id='sms5/SemanticID/5',
            score=round(random.uniform(0.1, 0.9), 1),
            meta_information={'matchSource': '1'}
        )

        matches = [match_1, match_2, match_3, match_4]

        score_limit = random.uniform(0.0, 0.3)
        json_util.save_as_json(self.test_json_path, matches)
        expected_matches = graph_util.find_reachable_matches('sms1/SemanticID/1', matches, score_limit)
        json_util.save_as_json(self.expected_matches_path, expected_matches)

        self.match_request = service_model.MatchRequest(
            semantic_id='sms1/SemanticID/1',
            score_limit=score_limit,
            local_only=False
        )
