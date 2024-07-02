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
            json.dump(data, f, indent=4, cls=CustomEncoder)  # indent=4 for pretty-printing

    except ValueError:
        print("Response content is not valid JSON")


def load_matches(path):
    def load_json(json_path):
        if os.path.isfile(json_path):
            try:
                with open(json_path, 'r') as file:
                    json_data = json.load(file, cls=CustomDecoder)
                    for match in json_data:
                        match.meta_information = None
                    return json_data
            except ValueError as e:
                print(f"Invalid JSON: {e}")
        elif os.path.isdir(json_path):
            json_data = []
            for file_name in os.listdir(json_path):
                if not file_name.endswith('.json'):
                    raise ValueError(f"{file_name} is not a JSON")
                file_path = os.path.join(json_path, file_name)
                with open(file_path, 'r') as json_file:
                    cur_json = json.load(json_file, cls=CustomDecoder)
                    json_data.extend(cur_json)
            for match in json_data:
                match.meta_information = None
            return json_data
        else:
            raise FileNotFoundError(f"{json_path} is not a file or directory")

    json_1 = load_json(path)
    if not isinstance(json_1, list) and all(isinstance(item, SemanticMatch) for item in json_1):
        raise TypeError
    sorted_list = sorted(json_1, key=lambda x: (x.base_semantic_id, x.match_semantic_id, x.score))
    return sorted_list


def check_sms(data_path):
    test_path = os.path.join(data_path, 'test', 'test.json')
    sms_path = os.path.join(data_path, 'SMS')  # Use SMS folder to construct big json
    return load_matches(test_path) == load_matches(sms_path)


def check_matches(data_path):
    retrieved_matches_path = os.path.join(data_path, 'test', 'retrieved_matches.json')
    expected_matches_path = os.path.join(data_path, 'test', 'expected_matches.json')
    expected_minimal_matches_path = os.path.join(data_path, 'test', 'minimal_matches.json')
    if os.path.isfile(expected_matches_path):
        if not load_matches(retrieved_matches_path) == load_matches(expected_matches_path):
            return False
    if os.path.isfile(expected_minimal_matches_path):
        retrieved_matches = load_matches(retrieved_matches_path)
        minimal_matches = load_matches(expected_minimal_matches_path)
        for match in minimal_matches:
            if match not in retrieved_matches:
                return False
    return True
