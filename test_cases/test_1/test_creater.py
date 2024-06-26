# This file stores methods to create and store different main cases as json in data/test_graphs
from semantic_matcher import service_model, model
import json
from model.Test import TestModel
from util import sms_util, graph_representation, json_util


def match_to_dict(match: model.SemanticMatch):
    return {
        "base_semantic_id": match.base_semantic_id,
        "match_semantic_id": match.match_semantic_id,
        "score": match.score,
        "meta_information": match.meta_information
    }


def save_as_json(file_path: str, matches_list): #TODO rename and integrate into main
    try:
        match_dict = {}
        # Convert the matches_list to a dictionary that can be serialized to JSON
        for match in matches_list:
            match_dict.setdefault(match.base_semantic_id, []).append(match_to_dict(match))

        # Write the JSON data to the file
        with open(file_path, 'w') as f:
            json.dump(match_dict, f, indent=4)  # indent=4 for pretty-printing

    except ValueError as e:
        print(f"Error saving JSON to {file_path}: {e}")


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
        save_as_json(self.test_path, matches_list)

    def run(self):
        sms_util.post_test_case(self.test_path, self.config)

    def evaluate(self):
        sms_util.get_all_sms(self.config)
        graph_representation.show_graph(self.data_SMS_path, self.data_image_path)
        if json_util.check_test(self.data_path):
            print("Test_1 worked correctly")
        else:
            raise AssertionError("Test_1 failed")
