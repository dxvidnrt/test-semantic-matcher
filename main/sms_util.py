import json
from resolver_modules import service as resolver_service
import requests
from semantic_matcher import service_model, model
import os
from main import json_util


def clear_all_sms(config):
    if 'ENDPOINTS' in config:
        for sms, endpoint in config["ENDPOINTS"].items():
            url = f'{endpoint}/clear'
            response = requests.post(url)


def get_all_sms(config):
    """
    Get all SMS stored in config and save graph as json in data folder.
    """
    for endpoint_name, endpoint_url in config['ENDPOINTS'].items():
        page = config['SMS']['url_get_all']
        url = f"{endpoint_url}/{page}"
        response = requests.get(url)
        if response.status_code == 200:
            if not endpoint_url.startswith("http://"):
                raise ValueError(f"Endpoint has wrong format: {endpoint_url}")
            endpoint_url = endpoint_url[len("http://"):]
            if not endpoint_url.endswith(":8000"):
                raise ValueError(f"Endpoint has wrong format: {endpoint_url}")
            name = endpoint_url[:-len(":8000")]

            file_path = f'./data/SMS/{name}.json'

            json_util.save_as_json(file_path, response)


def clear_all_sms(config):
    if 'ENDPOINTS' in config:
        for sms, endpoint in config["ENDPOINTS"].items():
            url = f'{endpoint}/clear'
            response = requests.post(url)


def post_test_case(file_path, config):
    """
    Post a main case defined by file_path to the corresponding SMS
    :param file_path:
    :return:
    """
    print("Clear all SMS")
    clear_all_sms(config)
    print(f"Filepath: {file_path}")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            matches_lists = {}

            for base_semantic_id, matches_data in data.items():
                matches = []
                for match_data in matches_data:
                    match = model.SemanticMatch(
                        base_semantic_id=match_data['base_semantic_id'],
                        match_semantic_id=match_data['match_semantic_id'],
                        score=match_data['score'],
                        meta_information=match_data['meta_information']
                    )
                    matches.append(match)
                if base_semantic_id not in matches_lists:
                    matches_lists[base_semantic_id] = service_model.MatchesList(matches=[])
                stored_matches = matches_lists[base_semantic_id].matches
                stored_matches.extend(matches)
                matches_lists[base_semantic_id] = service_model.MatchesList(matches=stored_matches)

        for base_semantic_id, matches_list in matches_lists.items():
            request_body = resolver_service.SMSRequest(semantic_id=base_semantic_id)
            endpoint = config['RESOLVER']['endpoint']
            port = config['RESOLVER'].getint('port')
            url = f"{endpoint}:{port}/get_semantic_matching_service"
            response = requests.get(url, json=request_body.dict())

            # Check if the response is successful (status code 200)
            if response.status_code == 200:
                # Parse the JSON response and construct SMSResponse object
                response_json = response.json()
                semantic_matching_service_endpoint = response_json['semantic_matching_service_endpoint']
                url = f"{semantic_matching_service_endpoint}/post_matches"
                response = requests.post(url, json=matches_list.dict())

    else:
        print(f"File '{file_path}' does not exist.")