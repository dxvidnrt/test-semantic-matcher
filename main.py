import requests


def example_match_request() -> dict:

    example_request = {
        "semantic_id": "s-heppner.com/semanticID/one",
        "score_limit": 0.5,
        "local_only": True,
        "name": "example_name",
        "definition": "example_definition"
    }
    return example_request

def example_match_post() -> dict:

    example_post = {
    "matches": [
        {
            "base_semantic_id": "s-heppner.com/semanticID/one",
            "match_semantic_id": "s-heppner.com/semanticID/3",
            "score": 0.8,
            "meta_information": {
                "matchSource": "Defined by David Niebert"
            }
        },
        {
            "base_semantic_id": "s-heppner.com/semanticID/3",
            "match_semantic_id": "s-heppner.com/semanticID/4",
            "score": 1.0,
            "meta_information": {
                "matchSource": "Defined by David Niebert"
            }
        },
    ]
    }
    return example_post


def main():

    url_get = "http://127.0.0.1:8001/get_matches"
    url_post = "http://127.0.0.1:8001/post_matches"
    req = example_match_request()

    # response_post = requests.post(url_post, json=example_match_post())
    response = requests.get(url_get, json=req)

    # print(response_post.json())
    print(response.text)


if __name__ == "__main__":
    main()
