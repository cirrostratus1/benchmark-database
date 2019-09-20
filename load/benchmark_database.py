# Copyright (c) 2019 fortiss GmbH
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import pandas as pd
import logging
import shutil
logging.getLogger().setLevel(logging.INFO)
import pickle
import zipfile

from modules.runtime.scenario.scenario_generation.scenario_generation import ScenarioGeneration
from serialization.scenario_set_serializer import ScenarioSetSerializer

FILE_EXTENSION_SCENARIO_SET = "bark_scenarios"

# The DatabaseSerializer recursively serializes all scenario param files sets
# within a folder and releases the whole database as zip file to github


class BenchmarkDatabase:
    def __init__(self, database_root):
        self.database_root = database_root
        if database_root.endswith("zip"):
            logging.info("extracting zipped-database {} to temporary directory /tmp/database".format(database_root))
            shutil.rmtree("/tmp/database")
            os.makedirs("/tmp/database")
            with zipfile.ZipFile(database_root, 'r') as zip_obj:
                zip_obj.extractall('/tmp/database')
            self.database_root = '/tmp/database'

        # parse recursively all info dictionaries in database into pandas table
        self.dataframe = pd.DataFrame()
        for root, dirs, files in os.walk(self.database_root):
            for file in files:
                if file == ScenarioSetSerializer.scenario_set_info_filename():
                    logging.info("Found info dict {}".format(file))
                    with open(os.path.join(root,file), "rb") as f:
                        info_dict = pickle.load(f)
                    self.dataframe = self.dataframe.append(info_dict, ignore_index=True)
        logging.info("The following scenario sets are available")
        print(self.dataframe.to_string())

    def get_scenario_generator(self, scenario_set_id):
        scenario_generation = ScenarioGeneration()

        serialized_file_name = self.dataframe.iloc[scenario_set_id]["Serialized"]
        serialized_file_path = os.path.join(self.database_root, serialized_file_name)
        scenario_generation.load_scenario_list(filename=serialized_file_path)

        return scenario_generation