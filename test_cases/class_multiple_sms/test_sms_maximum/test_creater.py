from semantic_matcher import service_model, model

from model.Test import TestModel
from util import json_util


class Test(TestModel):

    def __init__(self, name):
        super().__init__(name)
        self.start_server_name = None

    def create(self):

        semantic_ids = []
        semantic_id_count = 1

        matches_list = []
        minimal_matches = []

        start_semantic_id = None

        for sms in self.sms:
            semantic_id = f"{sms}/SemanticID/{semantic_id_count}"
            match = None
            for base_semantic_id in semantic_ids:
                match = model.SemanticMatch(
                    base_semantic_id=base_semantic_id,
                    match_semantic_id=semantic_id,
                    score=1,
                    meta_information={'matchSource': '1'}
                )
                matches_list.append(match)
            if semantic_id_count == 1:
                start_semantic_id = semantic_id
            if match is not None and len(self.sms) == semantic_id_count:
                minimal_matches.append(match)
            semantic_id_count += 1
            semantic_ids.append(semantic_id)

        json_util.save_as_json(self.test_json_path, matches_list)
        json_util.save_as_json(self.expected_minimal_matches_path, minimal_matches)

        if start_semantic_id is not None:
            self.match_request = service_model.MatchRequest(
                semantic_id=start_semantic_id,
                score_limit=1,
                local_only=False
            )
