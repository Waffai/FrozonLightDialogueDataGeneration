
import base64
import datetime

import ecdsa
import hashlib
import json

import requests




def sign(formatted_date: str, body: str, path: str) -> str:
    # 从 PEM 文件中读取私钥
    with open("eckey2.pem", "rb") as f:
        private_key = ecdsa.SigningKey.from_pem(f.read())

    # 将请求正文编码为字节序列
    body_bytes = body.encode('utf-8')

    # 计算请求正文的 SHA-256 哈希值
    hash_value = hashlib.sha256(body_bytes).digest()

    # 将哈希值编码为 Base64 格式的字符串
    base64_value = base64.b64encode(hash_value).decode('utf-8')

    # 构造待签名的消息
    message = f"{formatted_date}:{base64_value}:{path}".encode('utf-8')

    print("message:", message)
    # 使用私钥对消息进行签名
    signature = private_key.sign(message, hashfunc=hashlib.sha256, sigencode=ecdsa.util.sigencode_der)

    # 将签名结果编码为 Base64 格式的字符串
    signature_base64 = base64.b64encode(signature).decode('utf-8')

    return signature_base64


# POST [path]/database/[version]/[container]/[environment]/[database]/records/lookup



if __name__ == '__main__':
    keyID = "5e47fc724d2f042a10bfcf69144b147a4194c05fc78e5fa122733e6faeca45b3"
    path = "https://api.apple-cloudkit.com"
    subpath = "/database/1/iCloud.com.duskmount.lightfrozen.languagebuddy/development/public/records/lookup"
    # get current time
    formatted_date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    body = {
        "records": [
            {
                "recordName": "5e47fc724d2f042a10bfcf69144b147a4194c05fc78e5fa122733e6faeca45b3"
            }
        ]
    }

    bodyData = json.dumps(body, separators=(',', ':'))


    signature = sign(formatted_date, bodyData, subpath)


    # make a request
    response = requests.post(
        f"{path}{subpath}",
        headers={
            "Content-Type": "text/plain",
            "X-Apple-CloudKit-Request-KeyID": keyID,
            "X-Apple-CloudKit-Request-ISO8601Date": formatted_date,
            "X-Apple-CloudKit-Request-SignatureV1": signature,
        },
        data=bodyData,
    )

    print(response.text)




