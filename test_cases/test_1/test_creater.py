# This file stores methods to create and store different main cases as json in data/test_graphs
from semantic_matcher import service_model, model
import json
from model.Test import TestModel
from util import sms_util, graph_representation, json_util


class Test(TestModel):
    def create(self):
        match_sms_1 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/semanticID/1',
            match_semantic_id='dxvidnrt.com/semanticID/2',
            score=0.9,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        match_sms_2 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/semanticID/2',
            match_semantic_id='dxvidnrt.com/semanticID/3',
            score=0.9,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        match_sms_3 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/semanticID/3',
            match_semantic_id='dxvidnrt.com/semanticID/1',
            score=0.9,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        matches_list = [match_sms_1, match_sms_2, match_sms_3]
        json_util.save_as_json(self.test_json_path, matches_list)

    def run(self):
        sms_util.post_test_case(self.test_json_path, self.config)
