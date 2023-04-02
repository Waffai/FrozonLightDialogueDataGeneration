
import os
import time

from jobs_config import jobs_config

home_dir = os.path.expanduser("~")
input_dir = home_dir + jobs_config["data_directory"] + jobs_config["steps"]["clean_uploaded"][
    "input_directory"] + "/"
storage_time = jobs_config["storage_time"]


if __name__ == '__main__':
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




