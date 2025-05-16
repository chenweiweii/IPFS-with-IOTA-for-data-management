import os
import base64
import requests
from Crypto.Cipher import AES
from dotenv import load_dotenv
from iota import TryteString
from iota_sdk import Client

load_dotenv()
# Choose a IOTA node
node_url = os.environ.get('NODE_URL', 'https://api.stardust-mainnet.iotaledger.net')

# configure your own ipfs node or use a public one
host = "http://127.0.0.1:5001"
url_download = host + "/api/v0/cat"

# 32-byte shared key
SHARED_SECRET = '12345678901234567890123456789012'

# Function to get data to IPFS
def from_ipfs(cid: str) -> bytes:
    resp = requests.post(url_download, params={'arg': cid})
    resp.raise_for_status()
    return base64.b64decode(resp.text)

# 从 Receive data from the tangle
def from_iota() -> bytes:
    client = Client(nodes=[node_url])
    bid = input("Please enter the IOTA Block ID: ")
    hex_str = client.get_block_data(bid).payload.data
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    blob2_hex = bytes.fromhex(hex_str).decode('utf-8')
    return bytes.fromhex(blob2_hex)

# Functions to AES-GCM decryption
def decrypt_gcm(iv: bytes, tag: bytes, ct: bytes, secret: str) -> str:
    cipher = AES.new(secret.encode('utf-8'), AES.MODE_GCM, iv)
    plain = cipher.decrypt_and_verify(ct, tag)
    return plain.decode('utf-8')

if __name__ == '__main__':
    blob2 = from_iota()
    iv2, tag2, ct2 = blob2[:12], blob2[12:28], blob2[28:]
    trytes2 = decrypt_gcm(iv2, tag2, ct2, SHARED_SECRET)
    payload2 = TryteString(trytes2).decode()
    key1_str, cid1 = payload2.split('|', 1)
    print(f'IPFS CID: {cid1}')
    print(f'root1: {key1_str}')
    # get IPFS data
    ct1 = from_ipfs(cid1)
    iv1 = base64.b64decode(key1_str[:16])
    tag1 = base64.b64decode(key1_str[16:40])
    trytes1 = decrypt_gcm(iv1, tag1, ct1, SHARED_SECRET)
    original = TryteString(trytes1).decode()
    # print("\nDecoded message:\n", original)