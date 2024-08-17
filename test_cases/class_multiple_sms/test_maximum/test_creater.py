from semantic_matcher import service_model, model

from model.Test import TestModel
from util import json_util


class Test(TestModel):

    def create(self):

        matches_list = []
        minimal_matches = []

        match_request_semantic_id = None

        number_sms = len(self.sms)
        semantic_id_counter = 1
        if number_sms < 2:
            raise ValueError("Not enough SMS")

        # Create a path through all SMS and back to the start SMS
        for i in range(number_sms-1):
            sms_1, sms_2 = self.sms[i], self.sms[i+1]
            match_1 = model.SemanticMatch(
                base_semantic_id=f'{sms_1}/SemanticID/{semantic_id_counter}',
                match_semantic_id=f'{sms_2}/SemanticID/{semantic_id_counter+1}',
                score=1.0,
                meta_information={'matchSource': '1'}
            )
            match_2 = model.SemanticMatch(
                base_semantic_id=f'{sms_2}/SemanticID/{(2*number_sms)-semantic_id_counter+2}',
                match_semantic_id=f'{sms_1}/SemanticID/{(2*number_sms)-semantic_id_counter+1}',
                score=1.0,
                meta_information={'matchSource': '1'}
            )
            matches_list.append(match_1)
            matches_list.append(match_2)
            if semantic_id_counter == 1:
                match_request_semantic_id = f'{sms_1}/SemanticID/{semantic_id_counter}'
                minimal_matches.append(match_2)
            if semantic_id_counter == number_sms:
                match_3 = model.SemanticMatch(
                    base_semantic_id=f'{sms_2}/SemanticID/{semantic_id_counter+1}',
                    match_semantic_id=f'{sms_2}/SemanticID/{semantic_id_counter+2}',
                    score=1.0,
                    meta_information={'matchSource': '1'}
                )
                matches_list.append(match_3)

            semantic_id_counter += 1

        json_util.save_as_json(self.test_json_path, matches_list)
        json_util.save_as_json(self.expected_minimal_matches_path, minimal_matches)

        if match_request_semantic_id is not None:
            self.match_request = service_model.MatchRequest(
                semantic_id=match_request_semantic_id,
                score_limit=1,
                local_only=False
            )
