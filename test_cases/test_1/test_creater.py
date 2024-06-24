# This file stores methods to create and store different main cases as json in data/test_graphs
from semantic_matcher import service_model, model
import json

config_path = './config.ini.default'  # Use relative path within Docker container
data_path = './data'


def match_to_dict(match: model.SemanticMatch):
    return {
        "base_semantic_id": match.base_semantic_id,
        "match_semantic_id": match.match_semantic_id,
        "score": match.score,
        "meta_information": match.meta_information
    }


def save_as_json(file_path: str, matches_list): #TODO rename and integrate into util
    try:
        match_dict = {}
        # Convert the matches_list to a dictionary that can be serialized to JSON
        for match in matches_list:
            match_dict.setdefault(match.base_semantic_id, []).append(match_to_dict(match))

        # Write the JSON data to the file
        with open(file_path, 'w') as f:
            json.dump(match_dict, f, indent=4)  # indent=4 for pretty-printing

        print(f"Data saved to {file_path}")
    except ValueError as e:
        print(f"Error saving JSON to {file_path}: {e}")


def test_case_simple_circle():
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
    path = f'{data_path}/test.json'
    save_as_json(path, matches_list)
