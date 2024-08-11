from semantic_matcher import service_model, model

from model.Test import TestModel
from util import json_util


class Test(TestModel):

    def __init__(self, name):
        super().__init__(name)
        self.start_server_name = None

    def create(self):
        match_1 = model.SemanticMatch(
            base_semantic_id='sms1/semanticID/Dog',
            match_semantic_id='sms2/semanticID/Cat',
            score=0.7,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        match_2 = model.SemanticMatch(
            base_semantic_id='sms1/semanticID/Dog',
            match_semantic_id='sms3/semanticID/Dog',
            score=1,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        match_3 = model.SemanticMatch(
            base_semantic_id='sms3/semanticID/Dog',
            match_semantic_id='sms2/semanticID/Cat',
            score=0.8,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        match_4 = model.SemanticMatch(
            base_semantic_id='sms2/semanticID/Cat',
            match_semantic_id='sms4/semanticID/Bird',
            score=0.5,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        matches = [match_1, match_2, match_4, match_3]
        json_util.save_as_json(self.test_json_path, matches)
        self.match_request = service_model.MatchRequest(
            semantic_id='sms1/semanticID/Dog',
            score_limit=0,
            local_only=False
        )
