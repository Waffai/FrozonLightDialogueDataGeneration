import base64
import datetime
import hashlib
import json
import os
import random
import shutil
# generate a random string for random record name
import string
import time

import ecdsa
import requests

# read job-config.json into config
with open("jobs-config.json") as f:
    config = json.load(f)
cooling_time = config["cooling_time"]
print("cooling time: ", cooling_time)
# get input directory from config
# get home dir




if __name__ == '__main__':
    home_dir = os.path.expanduser("~")
    input_dir = home_dir + "/data/frozen_light_jobs/" + config["steps"]["clean_uploaded"]["input_directory"] + "/"
    storage_time = config["storage_time"]

    # get all files in input_dir
    files = os.listdir(input_dir)
    # get current time
    current_time = time.time()
    # get all files that are older than storage_time
    for file in files:
        file_path = input_dir + file
        file_time = os.path.getmtime(file_path)
        if current_time - file_time > storage_time:
            print("removing: ", file_path)
            os.remove(file_path)
    print("done")




