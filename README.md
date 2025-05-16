# IPFS with IOTA for data management

Data storing and sharing using IOTA Tangle and IPFS

This script realizes the following tasks:
1) Read a file (or files) from a local folder
2) Encode the content to Trytes with iota API and encrypt the Trytes using AES, return encrypted content and root1.
3) Upload encrypted content to the IPFS network and return a CID.
4) Encode and encrypt the CID and root1 with IOTA and AES, to create the payload.
5) Publish the payload to IOTA Tangle and return the block id.

to run the code: py publish.py

if you are using a local IPFS node, don't forget to start the host service first in a separate terminal: ipfs daemon 

Install the required dependencies and  by running the following commands:
pip install -r requirements.txt