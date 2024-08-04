import requests
from semantic_matcher import service_model, model
from resolver_modules import service as resolver_service

from model.Test import TestModel
from util import sms_util, graph_representation, json_util
import random


class Test(TestModel):

    def __init__(self, name):
        super().__init__(name)
        self.start_server_name = None

    def create(self):
        self.check_sms = False
        number_semantic_ids = random.randint(985, 985)

        matches_list = []
        minimal_matches = []
        last_match_semantic_id = f'sms1/semanticID/0'
        for i in range(number_semantic_ids):
            match_semantic_id = f'sms1/semanticID/{i+1}'
            match_i = model.SemanticMatch(
                base_semantic_id=last_match_semantic_id,
                match_semantic_id=match_semantic_id,
                score=1,
                meta_information={'matchSource': "1"}
            )
            matches_list.append(match_i)
            if i == number_semantic_ids - 1:
                minimal_matches.append(match_i)
            last_match_semantic_id = match_semantic_id

        json_util.save_as_json(self.test_json_path, matches_list)
        json_util.save_as_json(self.expected_minimal_matches_path, minimal_matches)

        self.match_request = service_model.MatchRequest(
            semantic_id='sms1/semanticID/0',
            score_limit=0,
            local_only=True
        )

        self.check_sms = False
