from semantic_matcher import model, service_model
from model.Test import TestModel
from util import sms_util, graph_representation, json_util
import random


class Test(TestModel):
    def create(self):
        # sms
        number_nodes = random.randint(15, 20)
        number_matches = random.randint(int((1/3) * (number_nodes ** 2)), int((2/3) * (number_nodes ** 2)))
        base_semantic_ids = [f"sms/SemanticId/{i}" for i in range(number_nodes)]
        matches = []
        for i in range(number_matches):
            match_i = model.SemanticMatch(
                base_semantic_id=random.choice(base_semantic_ids),
                match_semantic_id=random.choice(base_semantic_ids),
                score=random.uniform(0.000001, 1.0),
                meta_information={'matchSource': 'Defined by David Niebert'}
            )
            matches.append(match_i)
        json_util.save_as_json(self.test_json_path, matches)


