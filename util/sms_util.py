import json
from resolver_modules import service as resolver_service
import requests
from semantic_matcher import service_model, model
import os
from util import json_util


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
            response_json = response.json()
            equivalence_table = model.EquivalenceTable(matches=response_json)
            json_util.save_as_json(file_path, equivalence_table)


def clear_all_sms(config):
    if 'ENDPOINTS' in config:
        for sms, endpoint in config["ENDPOINTS"].items():
            url = f'{endpoint}/clear'
            response = requests.post(url)


def get_matches_sms(match_request, endpoint, path, config):
    page = config['SMS']['url_get']
    url = f'{endpoint}/{page}'
    print(f"URL: {url}")
    response = requests.get(url, json=match_request.dict())
    print(f"Response: {response}")
    response_json = response.json()
    print(f"Response_json: {response_json}")
    matches_list = response_json["matches"]
    json_util.save_as_json(path, matches_list)


def post_test_case(file_path, config):
    """
    Post a main case defined by file_path to the corresponding SMS
    :param file_path:
    :return:
    """
    clear_all_sms(config)

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            match_list = json.load(file, cls=json_util.CustomDecoder)
            print(match_list)
            matches_dict = {}
            for match in match_list:
                if isinstance(match, model.SemanticMatch):
                    base_semantic_id = match.base_semantic_id
                    if base_semantic_id not in matches_dict:
                        matches_dict[base_semantic_id] = []
                    matches_dict[base_semantic_id].append(match)
                else:
                    raise TypeError(f"{match} not of type SemanticMatch")

            for base_semantic_id, matches_list in matches_dict.items():
                print(f"Base sem id: {base_semantic_id}")
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
                    print(f"Semantic_matching_service_endpoint: {semantic_matching_service_endpoint}")
                    url = f"{semantic_matching_service_endpoint}/post_matches"
                    json_matches_list = json.dumps({'matches': matches_list}, indent=4, cls=json_util.CustomEncoder)
                    print("json_matches_list")
                    print(json_matches_list)
                    response = requests.post(url, data=json_matches_list, headers={'Content-Type': 'application/json'})

    else:
        print(f"File '{file_path}' does not exist.")
