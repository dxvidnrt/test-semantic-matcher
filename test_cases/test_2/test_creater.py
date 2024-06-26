from semantic_matcher import service_model, model
import json

from model.Test import TestModel
from util import sms_util, graph_representation, json_util

config_path = './config.ini.default'  # Use relative path within Docker container
data_path = './data'


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


def create_test():
    match_sms_1 = model.SemanticMatch(
        base_semantic_id='dxvidnrt.com/semanticID/1',
        match_semantic_id='dxvidnrt.com/semanticID/1',
        score=1,
        meta_information={'matchSource': 'Defined by David Niebert'}
    )
    matches_list = [match_sms_1]
    path = f'{data_path}/test.json'
    save_as_json(path, matches_list)


class Test(TestModel):
    def create(self):
        match_sms_1 = model.SemanticMatch(
            base_semantic_id='dxvidnrt.com/semanticID/1',
            match_semantic_id='dxvidnrt.com/semanticID/1',
            score=1,
            meta_information={'matchSource': 'Defined by David Niebert'}
        )
        matches_list = [match_sms_1]
        path = f'{data_path}/test.json'
        save_as_json(path, matches_list)

    def run(self):
        sms_util.post_test_case(self.test_path, self.config)

    def evaluate(self):
        sms_util.get_all_sms(self.config)
        graph_representation.show_graph(self.data_SMS_path, self.data_image_path)
        if json_util.check_test(self.data_path):
            print("Test_2 worked correctly")
        else:
            raise AssertionError("Test_2 failed")
