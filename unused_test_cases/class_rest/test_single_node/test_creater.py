from semantic_matcher import service_model, model
from model.Test import TestModel
from util import json_util


class Test(TestModel):
    def create(self):
        match_sms_1 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/semanticID/SingleNode',
            match_semantic_id='dxvidnrt.com/semanticID/SingleNode',
            score=0.5,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )

        json_util.save_as_json(self.test_json_path, [match_sms_1])
        json_util.save_as_json(self.expected_matches_path, [match_sms_1])
        self.match_request = service_model.MatchRequest(
            semantic_id="dxvidnrt.com/semanticID/SingleNode",
            score_limit=0.1,
            local_only=False
        )
