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


def running_in_docker():
    return os.path.exists('/.dockerenv')


if running_in_docker():
    config_path = './config.ini.default'  # Use relative path within Docker container
    data_path = './data'
    data_SMS_path = './data/SMS'
    image_path = './data/images'
else:
    config_path = '../config.ini.default'  # Use relative path when running on its own
    data_path = '../data'
    data_SMS_path = '../data/SMS'
    image_path = '../data/images'


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
            graph_image_path: str
    ):
        self.router = APIRouter()

        self.router.add_api_route(
            "/",
            self.read_root,
            methods=["GET"]
        )
        self.router.add_api_route(
            "/graph",
            self.represent_graph,
            methods=["GET"]
        )
        self.endpoint: str = endpoint
        self.data_SMS_path = data_SMS_path
        self.graph_image_path = graph_image_path

    def read_root(self):
        return {"message": "Hello, World!"}

    def represent_graph(self):
        graph_representation.show_graph(self.data_SMS_path, self.graph_image_path)
        return FileResponse("/data/images/graph.png")


def example_match_request() -> dict:

    example_match_request = service_model.MatchRequest(
        semantic_id="dxvidnrt.com/semanticID/myOne",
        score_limit=0.3,
        local_only=True,
        name="example_name",
        definition="example_definition"
    )
    return example_match_request.dict()


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


def main():
    os.makedirs('./data', exist_ok=True)
    os.makedirs('./data/SMS', exist_ok=True)
    os.makedirs('./data/images', exist_ok=True)
    # TODO Change all file_paths to differentiate between Docker and no Docker
    print("Created images")
    """   
    print("Starting...")
    wait_server()
    test_multiple_sms()
    # get_all_sms()

    graph_representation.show_graph(data_path, image_path)
    """
    TEST_SERVICE = TestService(
        endpoint=config['SERVICE']['endpoint'],
        data_path=data_SMS_path,
        graph_image_path=image_path
    )
    APP = FastAPI()
    APP.include_router(
        TEST_SERVICE.router
    )
    print(f"Starting server on host 0.0.0.0 and port {int(config['SERVICE']['PORT'])}")
    uvicorn.run(APP, host="0.0.0.0", port=int(config["SERVICE"]["PORT"]))


if __name__ == "__main__":
    main()
