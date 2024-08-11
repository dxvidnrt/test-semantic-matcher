from semantic_matcher import model, service_model
from model.Test import TestModel
from util import json_util


class Test(TestModel):
    def create(self):
        match_1 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/SemanticID/Local1',
            match_semantic_id='dxvidnrt.com/SemanticID/Local2',
            score=0.8,
            meta_information={'matchSource': 'Local'}
        )
        match_2 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/SemanticID/Local2',
            match_semantic_id='s-heppner.com/SemanticID/remote2',
            score=1,
            meta_information={'matchSource': 'Local'}
        )
        match_3 = model.SemanticMatch(
            base_semantic_id='s-heppner.com/SemanticID/remote2',
            match_semantic_id='s-heppner.com/SemanticID/remote3',
            score=0.8,
            meta_information={'matchSource': 'Remote'}
        )
        match_4 = model.SemanticMatch(
            base_semantic_id='s-heppner.com/SemanticID/remote4',
            match_semantic_id='dxvidnrt.com/SemanticID/local4',
            score=1,
            meta_information={'matchSource': 'Local'}
        )
        match_5 = model.SemanticMatch(
            base_semantic_id='s-heppner.com/SemanticID/remote3',
            match_semantic_id='s-heppner.com/SemanticID/remote4',
            score=0.9,
            meta_information={'matchSource': 'Remote'}
        )
        matches = [match_1, match_2, match_3, match_4, match_5]
        expected_matches = [match_1, match_2]
        json_util.save_as_json(self.test_json_path, matches)
        json_util.save_as_json(self.expected_matches_path, expected_matches)
        self.match_request = service_model.MatchRequest(
            semantic_id='dxvidnrt.com/SemanticID/Local1',
            score_limit=0.1,
            local_only=True
        )
