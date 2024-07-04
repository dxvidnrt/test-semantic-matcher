from semantic_matcher import model, service_model
from model.Test import TestModel
from util import sms_util, graph_representation, json_util


class Test(TestModel):
    def create(self):
        match_1 = model.SemanticMatch(
            base_semantic_id='uml1.com/semanticID/1',
            match_semantic_id='uml1.com/semanticID/2',
            score=0.8,
            meta_information={'matchSource': '1'}
        )
        match_2 = model.SemanticMatch(
            base_semantic_id='uml1.com/semanticID/1',
            match_semantic_id='uml2.com/semanticID/2',
            score=0.8,
            meta_information={'matchSource': '1'}
        )
        match_3 = model.SemanticMatch(
            base_semantic_id='uml1.com/semanticID/1',
            match_semantic_id='uml3.com/semanticID/3',
            score=0.8,
            meta_information={'matchSource': '1'}
        )
        match_4 = model.SemanticMatch(
            base_semantic_id='uml3.com/semanticID/3',
            match_semantic_id='uml5.com/semanticID/5',
            score=0.8,
            meta_information={'matchSource': '2'}
        )
        match_5 = model.SemanticMatch(
            base_semantic_id='uml1.com/semanticID/10',
            match_semantic_id='uml5.com/semanticID/5',
            score=0.8,
            meta_information={'matchSource': '1'}
        )
        match_6 = model.SemanticMatch(
            base_semantic_id='uml4.com/semanticID/12',
            match_semantic_id='uml4.com/semanticID/12',
            score=0.8,
            meta_information={'matchSource': '3'}
        )
        matches = [match_1, match_2, match_3, match_4, match_5, match_6]
        json_util.save_as_json(self.test_json_path, matches)
