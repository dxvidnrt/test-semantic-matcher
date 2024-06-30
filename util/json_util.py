import json
import os
from collections import Counter

from semantic_matcher.model import SemanticMatch, EquivalenceTable
from semantic_matcher.service_model import MatchRequest


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SemanticMatch):
            return {
                "base_semantic_id": obj.base_semantic_id,
                "match_semantic_id": obj.match_semantic_id,
                "score": obj.score,
                "meta_information": obj.meta_information
            }
        elif isinstance(obj, list) and all(isinstance(item, SemanticMatch) for item in obj):
            return [self.default(item) for item in obj]
        elif isinstance(obj, EquivalenceTable):
            concated_matches_list = []
            for _, matches_list in obj.matches.items():
                concated_matches_list.extend(matches_list)
            return concated_matches_list  # Return as Python list for further serialization
        elif isinstance(obj, MatchRequest):
            return {
                "semantic_id": obj.semantic_id,
                "score_limit": obj.score_limit,
                "local_only": obj.local_only,
                "name": obj.name,
                "definition": obj.definition
            }
        else:
            return super().default(obj)


class CustomDecoder(json.JSONDecoder):
    def decode(self, json_string):
        try:
            decoded_data = json.loads(json_string)
            matches = []

            # Iterate through each item in the decoded JSON data
            for item in decoded_data:
                # Check if the item has the expected keys for SemanticMatch
                if 'base_semantic_id' in item and 'match_semantic_id' in item and 'score' in item and 'meta_information' in item:
                    # Create a SemanticMatch instance from the item data
                    match = SemanticMatch(
                        base_semantic_id=item['base_semantic_id'],
                        match_semantic_id=item['match_semantic_id'],
                        score=item['score'],
                        meta_information=item['meta_information']
                    )
                    matches.append(match)
                else:
                    # Handle cases where the item does not match the expected SemanticMatch structure
                    print(f"Skipping item as it does not match SemanticMatch structure: {item}")
        except Exception:
            raise TypeError(f"JSON-String {json_string} is not of type List[SemanticMatch]")

        return matches


def save_as_json(file_path: str, data):
    try:

        # Write the JSON data to the file
        with open(file_path, 'w') as f:
            print(f"Data: {data}")
            json.dump(data, f, indent=4, cls=CustomEncoder)  # indent=4 for pretty-printing

    except ValueError:
        print("Response content is not valid JSON")


def compare_json(file_path_1, file_path_2):
    def load_json(path):
        if os.path.isfile(path):
            try:
                with open(path, 'r') as file:
                    return json.load(file, cls=CustomDecoder)
            except ValueError as e:
                print(f"Invalid JSON: {e}")
        elif os.path.isdir(path):
            json_data = []
            for file_name in os.listdir(path):
                if not file_name.endswith('.json'):
                    raise ValueError(f"{file_name} is not a JSON")
                file_path = os.path.join(path, file_name)
                with open(file_path, 'r') as json_file:
                    cur_json = json.load(json_file, cls=CustomDecoder)
                    json_data.extend(cur_json)
            return json_data
        else:
            raise FileNotFoundError(f"{path} is not a file or directory")

    json_1 = load_json(file_path_1)
    json_2 = load_json(file_path_2)
    print(f"Json1: {json_1}")
    print(f"Json2: {json_2}")
    if not isinstance(json_1, list) and all(isinstance(item, SemanticMatch) for item in json_1):
        raise TypeError
    if not isinstance(json_2, list) and all(isinstance(item, SemanticMatch) for item in json_2):
        raise TypeError
    sorted_list1 = sorted(json_1, key=lambda x: (x.base_semantic_id, x.match_semantic_id, x.score))
    sorted_list2 = sorted(json_2, key=lambda x: (x.base_semantic_id, x.match_semantic_id, x.score))
    # This will fail when only x.meta_information differs
    return sorted_list1 == sorted_list2


def check_sms(data_path):
    test_path = os.path.join(data_path, 'test', 'test.json')
    sms_path = os.path.join(data_path, 'SMS')  # Use SMS folder to construct big json
    return compare_json(test_path, sms_path)


def check_matches(data_path):
    retrieved_matches_path = os.path.join(data_path, 'test', 'retrieved_matches.json')
    expected_matches_path = os.path.join(data_path, 'test', 'expected_matches.json')
    return compare_json(retrieved_matches_path, expected_matches_path)
