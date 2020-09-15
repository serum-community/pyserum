import base64

from solana.publickey import PublicKey
from solana.rpc.api import Client


def load_bytes_data(addr: PublicKey, endpoint: str):
    res = Client(endpoint).get_account_info(addr)
    if ("result" not in res) or ("value" not in res["result"]) or ("data" not in res["result"]["value"]):
        raise Exception("Cannot load byte data.")
    data = res["result"]["value"]["data"][0]
    return base64.decodebytes(data.encode("ascii"))
