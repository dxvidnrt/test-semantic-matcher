import json

def save_as_json(file_path: str, response):
    try:
        # Parse the response content as JSON
        data = response.json()

        # Write the JSON data to the file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)  # indent=4 for pretty-printing

    except ValueError:
        print("Response content is not valid JSON")


def compare_json(file_path_1, file_path_2):
    def normalize_json(obj):
        """
        Recursively sort lists and dictionaries in the JSON object.
        """
        if isinstance(obj, dict):
            return {k: normalize_json(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return sorted(normalize_json(x) for x in obj)
        else:
            return obj

    try:
        with open(file_path_1, 'r') as file:
            json_1 = json.load(file)
        with open(file_path_1, 'r') as file:
            json_2 = json.load(file)
        return normalize_json(json_1) == normalize_json(json_2)
    except ValueError as e:
        print(f"Invalid JSON: {e}")
        return False


def check_test(data_path):
    # TODO Be able to merge result of multiple json SMS to be comparable to test_case
    # TODO work for all test cases
    test_path = f'{data_path}/test.json'
    sms_path = f'{data_path}/SMS/python-semantic-matcher_2.json' # Use SMS folder to construct big json
    return compare_json(test_path, sms_path)
