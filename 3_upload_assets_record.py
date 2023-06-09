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

from jobs_config import jobs_config
from config import config

home_dir = os.path.expanduser("~")
# input_dir -> home_dir + data_dir + input_dir
input_dir = home_dir + jobs_config["data_directory"] + jobs_config["steps"]["upload_records"]["input_directory"] + "/"
output_dir = home_dir + jobs_config["data_directory"] + jobs_config["steps"]["upload_records"]["output_directory"] + "/"
cooling_time = jobs_config["cooling_time"]

# if output_dir not exist, create it
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def sign(formatted_date_str: str, body_str: str, subpath_str: str) -> str:
    # 从 PEM 文件中读取私钥
    with open("eckey.pem", "rb") as f:
        private_key = ecdsa.SigningKey.from_pem(f.read())

    # 将请求正文编码为字节序列
    body_bytes = body_str.encode('utf-8')

    # 计算请求正文的 SHA-256 哈希值
    hash_value = hashlib.sha256(body_bytes).digest()

    # 将哈希值编码为 Base64 格式的字符串
    base64_value = base64.b64encode(hash_value).decode('utf-8')

    # 构造待签名的消息
    message = f"{formatted_date_str}:{base64_value}:{subpath_str}".encode('utf-8')

    print("message:", message)
    # 使用私钥对消息进行签名
    signature = private_key.sign(message, hashfunc=hashlib.sha256, sigencode=ecdsa.util.sigencode_der)

    # 将签名结果编码为 Base64 格式的字符串
    signature_base64 = base64.b64encode(signature).decode('utf-8')

    return signature_base64


# POST [path]/database/[version]/[container]/[environment]/[database]/records/lookup

def send_request(request_body_json, request_entity, request_action):
    keyID = config["cloudkit_keyID"]
    path = "https://api.apple-cloudkit.com"
    subpath = "/database/1/" + config["cloudkit_containerIdentifier"] + "/development/public/" + request_entity + "/" + request_action

    # get current time
    formatted_date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    body_text = json.dumps(request_body_json, separators=(',', ':'))
    print("body_text for sign and post as body: ", body_text)
    request_signature = sign(formatted_date, body_text, subpath)

    # make a request
    response = requests.post(
        f"{path}{subpath}",
        headers={
            "Content-Type": "text/plain",
            "X-Apple-CloudKit-Request-KeyID": keyID,
            "X-Apple-CloudKit-Request-ISO8601Date": formatted_date,
            "X-Apple-CloudKit-Request-SignatureV1": request_signature,
        },
        data=body_text,
    )
    return response


# https://developer.apple.com/library/archive/documentation/DataManagement/Conceptual/CloudKitWebServicesReference/UploadAssets.html#//apple_ref/doc/uid/TP40015240-CH8-SW1
# '''Request URLs
# To request URLs to upload asset data, compose a request similar to:
#
# curl -X POST '[path]/database/[version]/[container]/[environment]/[database]/assets/upload' -H 'content-type: application/json' -d '{
#   "tokens":[{
#       "recordType":"Artwork",
#       "fieldName":"image"
#     }]
# }'
# The response is:
#
# {
#   "tokens":[{
#         "recordName":"4c016e24-c397-4c9d-81d6-dee3e3a48bb0",
#         "fieldName":"image",
#         "url":[ASSET_UPLOAD_URL]
#     }]
# }


def request_url(record_name, record_type, asset_field_name):
    print("Start requesting url...")
    print("record_name: ", record_name)
    print("asset_field_name: ", asset_field_name)
    entity = "assets"
    action = "upload"
    body = {
        "tokens": [
            {
                "recordName": record_name,
                "recordType": record_type,
                "fieldName": asset_field_name
            }
        ]
    }

    response = send_request(body, entity, action)
    response_dict = json.loads(response.text)

    url = response_dict["tokens"][0]["url"]
    print("request_url finished! Returning url:", url)
    return url


# Upload Asset Data
# For each token dictionary in the response, upload the asset using a curl command similar to:
#
# curl -X POST $[ASSET_UPLOAD_URL] -d@[ASSET_FILE]
# The response is an asset dictionary, describe in Asset Dictionary, that you pass in a modify request.
#
# {
#   "singleFile" :{
#       "wrappingKey" : [WRAPPING_KEY],
#       "fileChecksum" : [SIGNATURE],
#       "receipt" : [RECEIPT],
#       "referenceChecksum" : [REFERENCE_CHECKSUM],
#       "size" : [SIZE]
#     }
# }


def upload_asset_data(record_name, url):
    print("Start uploading asset data...")
    print("record name:", record_name)
    print("url:", url)
    # get home dir

    data_file = input_dir + record_name + ".wav"

    # read file and convert it into blob
    with open(data_file, 'rb') as f:
        data = f.read()

    print("Request to upload...")
    response = requests.post(
        url,
        headers={
            "Content-Type": "text/plain",
        },
        data=data,
    )

    response_dict = json.loads(response.text)
    asset_dict = response_dict["singleFile"]

    print("upload_asset_data finished! Returning asset dict: ", asset_dict)
    print("response.text: ", response.text)

    return asset_dict


# Modify Records with Asset Fields
# Modify the records, described in Modifying Records (records/modify), setting the asset fields to the asset value dictionaries returned in the previous step. For example, create an Artist record setting the image asset to the uploaded file:
#
# curl -X POST '[path]/database/[version]/[container]/[environment]/[database]/records/modify' -H 'content-type: application/json' -d '{
#   "operations" :[{
#       "operationType" : "create",
#       "record" :{
#           "recordType" : "Artist",
#           "fields" :{
#               "title" : {"value" : "MacKerricher State Park"},
#               "artist" : {"value" : "Mei Chen"},
#               "image" : {
#                   "value" : {
#                       "wrappingKey" : [WRAPPING_KEY],
#                       "fileChecksum" : [FILE_CHECKSUM],
#                       "receipt" : [RECEIPT],
#                       "referenceChecksum" : [REFERENCE_CHECKSUM],
#                       "size": [SIZE]
#                    }
#               }
#           },
#           "recordName": "4c016e24-c397-4c9d-81d6-dee3e3a48bb0",
#           "desiredKeys": []
#       }
#   }]
# }'

def modify_record(record_name, asset_dict):
    print("Start modifying record...")
    print("record name:", record_name)
    print(asset_dict)
    entity = "records"
    action = "modify"

    # get record json from [record_name].json

    data_file = input_dir + record_name + ".json"
    with open(data_file, 'r') as f:
        record = json.load(f)

    #  asset_dict : "wrappingKey": [WRAPPING_KEY],
    #                       "fileChecksum" : [FILE_CHECKSUM],
    #                       "receipt" : [RECEIPT],
    #                       "referenceChecksum" : [REFERENCE_CHECKSUM],
    #                       "size": [SIZE]
    asset = {k: v for k, v in asset_dict.items() if v is not None}
    record["fields"]["audio"] = {"value": asset}

    body = {
        "operations": [{
            "operationType": "create",
            "record": record,
        }]
    }

    print("body.stringify(): ", json.dumps(body))
    response = send_request(body, entity, action)
    print(response.text)
    print("Uploading record completes.")


# def send_sample_request():
#     entity = "records"
#     action = "lookup"
#     body = {
#         "records": [
#             {
#                 "recordName": "5e47fc724d2f042a10bfcf69144b147a4194c05fc78e5fa122733e6faeca45b3"
#             }
#         ]
#     }
#
#     response = send_request(body, entity, action)
#     print(response.text)


def get_sentences_ready_to_upload():
    # get all files in the input directory
    files = os.listdir(input_dir)
    print("files: ", files)
    # get all files that are cooled (without file name extension)
    ready_to_upload_record_names = []
    for file in files:
        if file.endswith(".wav"):
            # get the file name (without extension)
            file_name = os.path.splitext(file)[0]
            # get the file creation time
            file_creation_time = os.path.getctime(input_dir + file)
            # get current time

            current_time = time.time()
            # check if the file is cooled
            if current_time - file_creation_time > cooling_time:
                ready_to_upload_record_names.append(file_name)
    print("ready_to_upload: ", ready_to_upload_record_names)
    return ready_to_upload_record_names


def get_dialogues_ready_to_upload():
    # get all files in the input directory
    files = os.listdir(input_dir)
    print("files: ", files)
    # get all files that are cooled (without file name extension)
    ready_to_upload_record_names = []
    for file in files:
        # if file type is not json, skip
        if not file.endswith(".json"):
            continue
        # load file content by json.load
        content = json.load(open(input_dir + file))
        if content["recordType"] == "Dialogues":
            # get the file name (without extension)
            file_name = os.path.splitext(file)[0]
            # get the file creation time
            file_creation_time = os.path.getctime(input_dir + file)
            # get current time
            current_time = time.time()
            # check if the file is cooled
            if current_time - file_creation_time > cooling_time:
                ready_to_upload_record_names.append(file_name)
    print("ready_to_upload: ", ready_to_upload_record_names)
    return ready_to_upload_record_names


def upload_dialogues_record(record):

    record_in_icloud = {
                            "recordType": "Dialogues",
                            "recordName": record["recordName"],
                            "fields": {
                                "scene": {"value": record["fields"]["dialogue_info"]["value"]["scene"]},
                                "keywords": {"value": ",".join(record["fields"]["dialogue_info"]["value"]["keywords"])},
                                "dialogue": {"value": record["fields"]["dialogue"]["value"]}
                            }
    }

    body = {
        "operations": [{
            "operationType": "create",
            "record": record_in_icloud
        }]
    }

    response = send_request(body, "records", "modify")
    print("response for upload dialogue", response.text)

if __name__ == '__main__':
    # 1. read and check if there are cooled audio file in the ready_to_upload dir; if there are, put their filename(record_name) in the ready_to_upload array
    ready_to_upload_sentences = get_sentences_ready_to_upload()
    if len(ready_to_upload_sentences) > 0:
        # 2. upload sentences with assets
        for record_name in ready_to_upload_sentences:
            print("Start uploading record: ", record_name)
            url = request_url(record_name, "Sentences", "audio")
            asset_dict = upload_asset_data(record_name, url)
            modify_record(record_name, asset_dict)

            # move audio file
            audio_file = input_dir + record_name + ".wav"
            shutil.move(audio_file, output_dir)
            # move json file
            json_file = input_dir + record_name + ".json"
            shutil.move(json_file, output_dir)
    else:
        print("There is no ready to upload sentence.")

    # 3. upload dialogue record
    ready_to_upload_dialogues = get_dialogues_ready_to_upload()
    if len(ready_to_upload_dialogues) > 0:
        for record_name in ready_to_upload_dialogues:
            #read json file
            data_file = input_dir + record_name + ".json"
            with open(data_file, 'r') as f:
                record = json.load(f)
            # upload dialogue record
            upload_dialogues_record(record)

            # move to file to output dir
            shutil.move(data_file, output_dir)

    else:
        print("There is no ready to upload dialogue.")
        exit(0)

    # 4. move the uploaded files (audio and json) into the uploaded dir
