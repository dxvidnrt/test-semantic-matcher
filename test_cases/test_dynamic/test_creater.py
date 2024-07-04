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
        services = list(self.config['ENDPOINTS'].keys())
        number_semantic_ids = random.randint(30, 40)
        sms_list = [str(i) for i in range(random.randint(5, 7))]

        matches_list = []
        expected_matches = []
        minimal_matches = []
        last_match_semantic_id = f'{random.choice(services)}/semanticID/0'
        self.start_server_name = last_match_semantic_id
        for i in range(number_semantic_ids):
            match_semantic_id = f'{random.choice(services)}/semanticID/{i+1}'
            match_i = model.SemanticMatch(
                base_semantic_id=last_match_semantic_id,
                match_semantic_id=match_semantic_id,
                score=1,
                meta_information={'matchSource': random.choice(sms_list)}
            )
            matches_list.append(match_i)
            expected_matches.append(match_i)
            if i % 2 == 0:
                minimal_matches.append(match_i)
            last_match_semantic_id = match_semantic_id

            json_util.save_as_json(self.test_json_path, matches_list)
            json_util.save_as_json(self.expected_matches_path, expected_matches)
            json_util.save_as_json(self.expected_minimal_matches_path, minimal_matches)

            self.match_request = service_model.MatchRequest(
                semantic_id=self.start_server_name,
                score_limit=0,
                local_only=False
            )
