import requests
from semantic_matcher import service_model, model
import graph_representation
import configparser
import time
import json
import os
from fastapi import APIRouter, FastAPI, File, HTTPException
import uvicorn
from fastapi.responses import FileResponse
from resolver_modules import service as resolver_service


def running_in_docker():
    return os.path.exists('/.dockerenv')


if running_in_docker():
    config_path = './config.ini.default'  # Use relative path within Docker container
    data_path = './data'

else:
    config_path = '../config.ini.default'  # Use relative path when running on its own
    data_path = '../data'

data_SMS_path = f'{data_path}/SMS'
data_image_path = f'{data_path}/images'
test_graphs_path = f'{data_path}/test_graphs'


config = configparser.ConfigParser()

config.read(config_path)

sms1_address_post = f"{config['ENDPOINTS']['sms1']}/{config['SMS']['url_post']}"
sms1_address_get = f"{config['ENDPOINTS']['sms1']}/{config['SMS']['url_get']}"

sms2_address_post = f"{config['ENDPOINTS']['sms2']}/{config['SMS']['url_post']}"
sms2_address_get = f"{config['ENDPOINTS']['sms2']}/{config['SMS']['url_get']}"


class TestService:
    def __init__(
            self,
            endpoint: str,
            data_SMS_path: str,
            data_image_path: str
    ):
        self.router = APIRouter()

        self.router.add_api_route(
            "/",
            self.represent_graph,
            methods=["GET"]
        )

        self.endpoint: str = endpoint
        self.data_SMS_path = data_SMS_path
        self.data_image_path = data_image_path

    def represent_graph(self):
        graph_representation.show_graph(self.data_SMS_path, self.data_image_path)
        return FileResponse(f"{data_image_path}/graph.png")


def example_match_request() -> dict:
    example_request = service_model.MatchRequest(
        semantic_id="dxvidnrt.com/semanticID/myOne",
        score_limit=0.3,
        local_only=True,
        name="example_name",
        definition="example_definition"
    )
    return example_request.dict()


def example_match_post() -> dict:
    match1 = model.SemanticMatch(
        base_semantic_id='dxvidnrt.com/semanticID/myOne',
        match_semantic_id='dxvidnrt.com/semanticID/my1',
        score=1.0,
        meta_information={'matchSource': 'Defined by David Niebert'}
    )
    match2 = model.SemanticMatch(
        base_semantic_id='dxvidnrt.com/semanticID/myOne',
        match_semantic_id='dxvidnrt.com/semanticID/my2',
        score=0.5,
        meta_information={'matchSource': 'Defined by David Niebert'}
    )
    match3 = model.SemanticMatch(
        base_semantic_id='dxvidnrt.com/semanticID/myOne',
        match_semantic_id='s-heppner.com/semanticID/one',
        score=0.5,
        meta_information={'matchSource': 'Defined by David Niebert'}
    )
    match4 = model.SemanticMatch(
        base_semantic_id='dxvidnrt.com/semanticID/my2',
        match_semantic_id='s-heppner.com/semanticID/almostMyTwo',
        score=0.9,
        meta_information={'matchSource': 'Defined by David Niebert'}
    )
    match4 = model.SemanticMatch(
        base_semantic_id='s-heppner.com/semanticID/2',
        match_semantic_id='s-heppner.com/semanticID/almostHisTwo',
        score=0.9,
        meta_information={'matchSource': 'Defined by David Niebert'}
    )
    matches_list = service_model.MatchesList(matches=[match1, match2, match3, match4]).dict()
    return matches_list


def basic_test():
    url_get = "http://127.0.0.1:8000/get_matches"
    url_post = "http://127.0.0.1:8000/post_matches"
    url_get_all = "http://127.0.0.1:8000/all_matches"

    response = requests.get(url_get_all)
    # print(response.text)
    response = requests.get(url_get, json=example_match_request())
    # print(f"Request before adding: {response.text}")
    response = requests.post(url_post, json=example_match_post())
    # print(f"Added: {example_match_post()}")
    response = requests.get(url_get_all)
    graph_representation.show_sms(response.json())
    # print(response.text)
    response = requests.get(url_get, json=example_match_request())
    print(f"Request after adding: {response.text}")


def save_as_json(file_path: str, response):
    try:
        # Parse the response content as JSON
        data = response.json()

        # Write the JSON data to the file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)  # indent=4 for pretty-printing

        print(f"Data saved to {file_path}")
    except ValueError:
        print("Response content is not valid JSON")


def test_multiple_sms():
    match_sms_1 = model.SemanticMatch(
        base_semantic_id='s-heppner.com/semanticID/seb_1',
        match_semantic_id='dxvidnrt.com/semanticID/dav_1',
        score=0.8,
        meta_information={'matchSource': 'Defined by David Niebert'}
    )
    matches_list = service_model.MatchesList(matches=[match_sms_1]).dict()
    response = requests.post(sms1_address_post, json=matches_list)
    print(f"Post to SMS1 {response.status_code}")

    match_sms_2 = model.SemanticMatch(
        base_semantic_id='dxvidnrt.com/semanticID/dav_1',
        match_semantic_id='dxvidnrt.com/semanticID/dav_2',
        score=0.5,
        meta_information={'matchSource': 'Defined by David Niebert'}
    )
    matches_list = service_model.MatchesList(matches=[match_sms_2]).dict()
    response = requests.post(sms2_address_post, json=matches_list)
    print(f"Post to SMS2 {response.status_code}")

    req_sms_1 = service_model.MatchRequest(
        semantic_id='s-heppner.com/semanticID/seb_1',
        score_limit=0.3,
        local_only=False,
        name="test_remote",
        definition="test_remote"
    )
    response = requests.get(sms1_address_get, json=req_sms_1.dict())

    if response.status_code == 200:
        file_path = 'data/response.json'

        save_as_json(file_path, response)
    else:
        print(f"Request failed with status code {response.status_code}")
        print("Response text:", response.text)


def get_all_sms():
    """
    Get all SMS stored in config and save graph as json in data folder.
    """
    print(("Start get_all_sms"))
    for endpoint_name, endpoint_url in config['ENDPOINTS'].items():
        print(f"SMS: {endpoint_name}")
        page = config['SMS']['url_get_all']
        url = f"{endpoint_url}/{page}"
        print(f"URL: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            print("200")
            if not endpoint_url.startswith("http://"):
                raise ValueError(f"Endpoint has wrong format: {endpoint_url}")
            endpoint_url = endpoint_url[len("http://"):]
            if not endpoint_url.endswith(":8000"):
                raise ValueError(f"Endpoint has wrong format: {endpoint_url}")
            name = endpoint_url[:-len(":8000")]

            file_path = f'data/SMS/{name}.json'

            save_as_json(file_path, response)


def wait_server():
    tries = 0
    max_tries = 10
    if 'ENDPOINTS' in config:
        semantic_server_list = list(config['ENDPOINTS'].items())
        while len(semantic_server_list) != 0:
            if tries > max_tries:
                raise ConnectionError("Exceeded max tries to connect")
            tries += 1
            for name, url in semantic_server_list:
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        semantic_server_list.remove((name, url))
                except requests.exceptions.RequestException as e:
                    print(f"Error connecting to {url}: {e}")
            time.sleep(1)
    else:
        raise ConnectionError("No Endpoints found")


def post_graphs(file_path):
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
                print(f"Stored_matches: {stored_matches}")
                stored_matches.extend(matches)
                print(f"Matches: {matches_lists}")
                matches_lists[base_semantic_id] = service_model.MatchesList(matches=stored_matches)

        print(f"Matches lists: {matches_lists}")
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
                print(f"Response: {response.status_code}")

    else:
        print(f"File '{file_path}' does not exist.")

# TODO Save graph tests as json in a folder


def main():
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(data_SMS_path, exist_ok=True)
    os.makedirs(data_image_path, exist_ok=True)
    print("Starting...")
    wait_server()
    test_multiple_sms()
    get_all_sms()
    post_graphs(f'{test_graphs_path}/test_graph.json')

    TEST_SERVICE = TestService(
        endpoint=config['SERVICE']['endpoint'],
        data_SMS_path=data_SMS_path,
        data_image_path=data_image_path
    )
    APP = FastAPI()
    APP.include_router(
        TEST_SERVICE.router
    )
    TEST_SERVICE.represent_graph()
    print(f"Starting server on host 0.0.0.0 and port {int(config['SERVICE']['PORT'])}")
    uvicorn.run(APP, host="0.0.0.0", port=int(config["SERVICE"]["PORT"]))


if __name__ == "__main__":
    main()
