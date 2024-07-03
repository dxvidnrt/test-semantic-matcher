from semantic_matcher import model, service_model
from model.Test import TestModel
from util import sms_util, graph_representation, json_util


class Test(TestModel):
    def create(self):
        match_1 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/semanticID/Dog',
            match_semantic_id='s-heppner.com/semanticID/NoDog',
            score=0,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        match_2 = model.SemanticMatch(
            base_semantic_id='s-heppner.com/semanticID/NoDog',
            match_semantic_id='s-heppner.com/semanticID/Cat_2',
            score=0.9,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        match_3 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/semanticID/Dog',
            match_semantic_id='s-heppner.com/semanticID/Fish',
            score=0.3,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        matches_list = [match_1, match_2, match_3]
        json_util.save_as_json(self.test_json_path, matches_list)

        minimal_matches = [match_2]
        json_util.save_as_json(self.expected_minimal_matches_path, minimal_matches)

        self.match_request = service_model.MatchRequest(
            semantic_id='dxvidnrt.com/semanticID/Dog',
            score_limit=0,
            local_only=False
        )

