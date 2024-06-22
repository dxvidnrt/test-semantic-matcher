import configparser
import os
from main import graph_representation, json_util, sms_util
import test_creater

config_path = './config.ini.default'
data_path = './data'
data_SMS_path = f'{data_path}/SMS'
data_image_path = f'{data_path}/images'
test_graphs_path = f'{data_path}/test_graphs'

config = configparser.ConfigParser()

config.read(config_path)


def main():
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(data_SMS_path, exist_ok=True)
    os.makedirs(data_image_path, exist_ok=True)  # TODO check if do in start_all
    sms_util.clear_all_sms(config)
    test_creater.test_case_simple_circle()
    test_path = f'{data_path}/simple_circle.json'  # TODO Name test in every test_i folder
    sms_util.post_test_case(test_path, config)
    sms_util.get_all_sms(config)
    graph_representation.show_graph(f'{data_path}/SMS', f'{data_path}/images')
    if json_util.check_test(data_path):
        print("Test_1 worked correctly")
    else:
        raise AssertionError("Test_1 failed")


if __name__ == "__main__":
    main()
