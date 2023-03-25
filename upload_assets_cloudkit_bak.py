import base64
import datetime
import os
import random

import ecdsa
import hashlib
import json
import requests

# generate a random string for random record name
import string


def random_record_name(length=10):
    """Generate a random string of lowercase letters and digits."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def sign(formatted_date_str: str, body_str: str, subpath_str: str) -> str:
    # 从 PEM 文件中读取私钥
    with open("eckey2.pem", "rb") as f:
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
    keyID = "5e47fc724d2f042a10bfcf69144b147a4194c05fc78e5fa122733e6faeca45b3"
    path = "https://api.apple-cloudkit.com"
    subpath = "/database/1/iCloud.com.duskmount.lightfrozen.languagebuddy/development/public/" + request_entity + "/" + request_action

    # get current time
    formatted_date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # body = {
    #     "records": [
    #         {
    #             "recordName": "5e47fc724d2f042a10bfcf69144b147a4194c05fc78e5fa122733e6faeca45b3"
    #         }
    #     ]
    # }

    body_text = json.dumps(request_body_json, separators=(',', ':'))

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


def request_url(record_name, asset_field_name):
    print("Start requesting url...")
    print("record_name: ", record_name)
    print("asset_field_name: ", asset_field_name)
    entity = "assets"
    action = "upload"
    body = {
        "tokens": [
            {
                "recordName": record_name,
                "recordType": "Questions",
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
    home_dir = os.path.expanduser("~")
    input_dir = home_dir + "/data/frozen_light_jobs/ready_to_upload/"
    data_file = input_dir + "6c1831d23a707e34b43d8827f7ea58a3" + ".wav"
    # data_file = input_dir + record_name + ".wav"

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
    record_type = "Questions"

    entity = "records"
    action = "modify"
    body = {
        "operations": [{
            "operationType": "create",
            "record": {
                "recordType": record_type,
                "fields": {
                    "question": {"value": "What is the meaning of life?"},
                    "difficulty": {"value": 1},
                    "audio": {
                        "value": asset_dict
                    }
                },
                "recordName": record_name

            }
        }]
    }

    response = send_request(body, entity, action)
    response_dict = json.loads(response.text)
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


if __name__ == '__main__':
    print("hello world")
    record_name = random_record_name()
    url = request_url(record_name, "audio")
    asset_dict = upload_asset_data(record_name, url)
    modify_record(record_name, asset_dict)
