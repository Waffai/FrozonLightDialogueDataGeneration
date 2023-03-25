import base64
import datetime

import ecdsa
import hashlib
import json
import requests


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


def send_request_save_record_with_asset_request_url():
    entity = "assets"
    action = "upload"
    body = {
        "tokens": [
            {
                "recordName": "5e47",
                "recordType": "Questions",
                "fieldName": "audio"
            }
        ]
    }

    response = send_request(body, entity, action)
    print("response.text: ", response.text)
    return response.url

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

def send_request_save_record_with_asset_upload_asset_data(url):

# # get config from reading jobs-config.json
#     jobs_config = readfile("jobs-config.json")

    input_dir = "/home/woo/data/frozen_light_jobs/ready_to_upload/"
    recordName = "01c4eb03e4c596b0f7db6fc8642f98da"
    data_file = input_dir + recordName + ".wav"

    token_dict = {
    "recordName": "5e47",
    "fieldName": "audio",
    "url": "https://cws.icloud-content.com:443/AuLBz8cBkmOOXapOQtJrmJ_ZQHe4WLQATAErmrGK7Olj5ZefAzYaZCJZyXEBLi9eK-jChzhcQLusc-VxxJH_TneuJR-xC65FD-vw8dyriDwz/singleFileUpload?tk=CAogz-ufwPok9sOH2fvstJeZXDk8IdK_SLvC8YGwq1YFI-YSmAEQ5-Hit_EwGOfRlYryMCIBBCoLAQEDASAD_0cVFYlggICAZGpLS5nxkfx_aGKZ2iiwAlsQImpSV_qTSH-h0frZdZ7v6RcOiQLKtA5_6EVnucmF7vEyJglLTTOURqrHx7JWs9dwZg-fajChMv8hT26VciYrnvEsao1IvgZtIukp_IA_flY3oLMngOPNY_gBSvzn4W0-goJAkg&c=iCloud.com.duskmount.lightfrozen.languagebuddy&z=_defaultZone&uuid=ea240794-eca5-48af-944a-4e4e84bb6b98&dataclass=com.apple.Dataclass.CloudKit&req=1385265414&p=43"
    }

    # read file and convert it into blob
    with open(data_file, 'rb') as f:
        data = f.read()


    response = requests.post(
        url,
        headers={
    "Content-Type": "text/plain",
    },
        data=data,
    )
    print("request: ", response.request)

    print("response: ", response.text)
    return response.text



def send_sample_request():
    entity = "records"
    action = "lookup"
    body = {
        "records": [
            {
                    "recordName": "5e47fc724d2f042a10bfcf69144b147a4194c05fc78e5fa122733e6faeca45b3"
            }
        ]
    }

    response = send_request(body, entity, action)
    print(response.text)


if __name__ == '__main__':
    print("hello world")
    url = send_request_save_record_with_asset_request_url()
    send_request_save_record_with_asset_upload_asset_data(url)
