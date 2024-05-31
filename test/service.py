import requests
from semantic_matcher import service_model, model
import graph_representation
import configparser

config = configparser.ConfigParser()

config.read('config.ini.default')

sms1_address_post = f"{config['SERVICE']['endpoint']}:{config['PORTS'].getint('sms1')}/{config['SMS']['url_post']}"
sms1_address_get = f"{config['SERVICE']['endpoint']}:{config['PORTS'].getint('sms1')}/{config['SMS']['url_get']}"

sms2_address_post = f"{config['SERVICE']['endpoint']}:{config['PORTS'].getint('sms2')}/{config['SMS']['url_post']}"
sms2_address_get = f"{config['SERVICE']['endpoint']}:{config['PORTS'].getint('sms2')}/{config['SMS']['url_get']}"


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


def test_multiple_sms():
    match_sms_1 = model.SemanticMatch(
        base_semantic_id='s-heppner.com/semanticID/seb_1',
        match_semantic_id='dxvidnrt.com/semanticID/dav_1',
        score=0.8,
        meta_information={'matchSource': 'Defined by David Niebert'}
    )
    matches_list = service_model.MatchesList(matches=[match_sms_1]).dict()
    response = requests.post(sms1_address_post, json=matches_list)
    print(f"Post seb_1, dav_1): {response.text}")

    req_sms_1 = service_model.MatchRequest(
        semantic_id='s-heppner.com/semanticID/seb_1',
        score_limit=0.3,
        local_only=False,
        name="test_remote",
        definition="test_remote"
    )
    response = requests.get(sms1_address_get, req_sms_1.dict())
    print(f"Get seb_1, dav_1: {response.text}")


def main():
    test_multiple_sms()


if __name__ == "__main__":
    main()
