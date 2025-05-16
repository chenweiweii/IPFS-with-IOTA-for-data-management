import os
import base64
import time
import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from dotenv import load_dotenv
from iota import TryteString
from iota_sdk import Client, utf8_to_hex

load_dotenv()
# Choose a IOTA node, you can find public nodes here: https://wiki.iota.org/build/networks-endpoints/
# for testing, you can use the https://api.testnet.iotaledger.net
node_url = os.environ.get('NODE_URL', 'https://api.stardust-mainnet.iotaledger.net')

# configure your own ipfs node or use a public one
host = "http://127.0.0.1:5001"
url_upload = host + "/api/v0/add"

# 32-byte shared key
SHARED_SECRET = '12345678901234567890123456789012'

# Functions to add data to IPFS
def add2ipfs(b64_payload: str) -> str:
    resp = requests.post(url_upload, files={'file': b64_payload})
    resp.raise_for_status()
    return resp.json()['Hash']

# Functions to AES-GCM encryption
def encrypt_gcm(plaintext: str, secret: str):
    iv = get_random_bytes(12)
    cipher = AES.new(secret.encode(), AES.MODE_GCM, iv)
    ct, tag = cipher.encrypt_and_digest(plaintext.encode())
    return iv, tag, ct

# Functions to add data to IOTA
def submit_to_iota(tag: str, message: str) -> str:
    client = Client(nodes=[node_url])
    tag_hex = utf8_to_hex(tag)
    message_hex = utf8_to_hex(message)
    block_id = client.build_and_post_block(
        secret_manager=None,
        tag=tag_hex,
        data=message_hex
    )
    return block_id

def publish():
    jsonpath = './test_samples/'
    for i in range(1, 4):
        full_path = os.path.join(jsonpath, f'case{i}.owl')
        # full_path = os.path.join(jsonpath, f'test_{i}K.owl')
        with open(full_path, 'r', encoding='utf-8') as file:
            raw = file.read()

        trytes1 = str(TryteString.from_unicode(raw))
        # print(f'Trytes1: {trytes1}')

        # upload payload to IPFS
        t0 = time.time()
        iv1, tag1, ct1 = encrypt_gcm(trytes1, SHARED_SECRET)
        ct1_b64 = base64.b64encode(ct1).decode()
        # print(f'Payload:{ct1_b64}')
        cid1 = add2ipfs(ct1_b64)
        # print(f'IPFS_HASH:{cid1}')
        t1 = time.time()
        print(f'\nIPFS storing time: {(t1 - t0)*1000:.0f}')

        iv1_b64 = base64.b64encode(iv1).decode()
        tag1_b64 = base64.b64encode(tag1).decode()
        key1 = iv1_b64 + tag1_b64 + SHARED_SECRET
        # print(f'Root1:{key1}')
        print(f'IPFS hash and root1: {cid1} {key1}')

        # Encrypt hash and root1 and publish to IOTA Tangle
        payload2 = f'{key1}|{cid1}'
        trytes2 = str(TryteString.from_unicode(payload2))
        # print(f'IPFS_Trytes:{trytes2}')
        iv2, tag2, ct2 = encrypt_gcm(trytes2, SHARED_SECRET)
        blob2_hex = (iv2 + tag2 + ct2).hex()
        bid = submit_to_iota('', blob2_hex)
        t2 = time.time()
        print(f'IOTA Block ID: {bid[0]}')
        print(f'IOTA attaching time: {(t2 - t0) * 1000:.0f}')
        # time.sleep(5)

        print(f'IPFS_Payload:{blob2_hex}')

if __name__ == '__main__':
    publish()