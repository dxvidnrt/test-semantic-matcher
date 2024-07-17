from semantic_matcher import model, service_model
from model.Test import TestModel
from util import sms_util, graph_representation, json_util


class Test(TestModel):
    def create(self):
        match_1 = model.SemanticMatch(
            base_semantic_id='s-heppner.com/SemanticID/1',
            match_semantic_id='dxvidnrt.com/SemanticID/2',
            score=1,
            meta_information={'matchSource': '1'}
        )
        match_2 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/SemanticID/2',
            match_semantic_id='s-heppner.com/SemanticID/1',
            score=1,
            meta_information={'matchSource': '1'}
        )
        json_util.save_as_json(self.test_json_path, [match_1, match_2])
        json_util.save_as_json(self.expected_minimal_matches_path, [match_2])

        self.match_request = service_model.MatchRequest(
            semantic_id='s-heppner.com/SemanticID/1',
            score_limit=0,
            local_only=False
        )

