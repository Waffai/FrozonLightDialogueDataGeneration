import base64
import hashlib  # This is a sample Python script.
import json

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import requests
from requests_cloudkit import CloudKitAuth
import restmapper
import ecdsa


def make_signature(formatted_date, body, path):
    """
    See: "Accessing CloudKit Using a Server-to-Server Key"
    """
    PEM = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIGbCJbRh9ClQ24e8DrS+Sv5VVq5aCUqIMPsCDV7u9m7toAoGCCqGSM49
AwEHoUQDQgAEqcq27iKEnS2p1D4PedLUXNcowwl+heC4Xct8DXpIa5NTS+TbRzBX
laIJ2qVJutoj4pQLPACioHxM5tF4EE+AAQ==
-----END EC PRIVATE KEY-----"""

    to_sign = "{}:{}:{}".format(formatted_date,
                                encode_body(body),
                                path)

    sk = ecdsa.SigningKey.from_pem(PEM)
    signature = sk.sign(to_sign.encode(),
                        hashfunc=hashlib.sha256,
                        sigencode=ecdsa.util.sigencode_der)

    return base64.b64encode(signature)


def encode_body(body):
    """
    Return the request body. This is the base64 string encoded
    SHA-256 hash of the body.
    """
    if body is None:
        body = ""
    elif type(body) != str:
        body = json.dumps(body, separators=(',', ':'))

    h = hashlib.sha256(body.encode())
    return base64.b64encode(h.digest()).decode()


def print_hi(name):
    formatted_date = "2023-03-23T13:20:09Z"
    body = {"operations": [{"operationType": "create", "record": {"recordType": "Questions"}}]}
    path = "/database/1/iCloud.com.duskmount.lightfrozen.languagebuddy/development/public/records/modify"

    signature = make_signature(formatted_date, body, path)

    print(signature)
    print("MEUCIQCtsnGx73EIMtI+dYLEvwT8pUCno0LTR5moQ3jDUy8Y/QIgIsWkmTWak0k/kMNJmW4mVciVOlhaYoC0T7LG2Csm32o=")


if __name__ == '__main__':
    print_hi('PyCharm')
    #
    # YOUR_KEY_ID = "5e47fc724d2f042a10bfcf69144b147a4194c05fc78e5fa122733e6faeca45b3"
    # YOUR_PRIVATE_KEY_PATH = "eckey.pem"
    # auth = CloudKitAuth(key_id=YOUR_KEY_ID, key_file_name=YOUR_PRIVATE_KEY_PATH)
    # host = "https://api.apple-cloudkit.com"
    # path = "/database/1/iCloud.com.duskmount.lightfrozen.languagebuddy/development/public/records/modify"
    # requests.post(host + path, auth=auth)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
