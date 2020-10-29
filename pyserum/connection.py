import json

from solana.rpc.api import Client as conn  # pylint: disable=unused-import
from solana.rpc.providers.http import requests

from .market.types import MarketInfo


def get_live_markets():
    url = "https://raw.githubusercontent.com/project-serum/serum-js/master/src/tokens_and_markets.ts"
    resp = requests.get(url)
    page = resp.text

    # Turn this JS into json
    data = page.split("MARKETS:")[1].split("}> = ")[1].split(";")[0]
    data = data.replace(" new PublicKey(", "").replace(")", "")
    for col in ["name", "address", "programId", "deprecated"]:
        data = data.replace(col, '"{}"'.format(col))
    data = data.replace("'", '"')
    data = data.replace(" ", "")
    data = data.replace("\n", "")
    data = data.replace(",}", "}")
    data = data.replace(",]", "]")
    data = json.loads(data)

    markets = []
    for raw in data:
        if raw["deprecated"]:
            continue
        markets.append(MarketInfo(name=raw["name"], address=raw["address"], program_id=raw["programId"]))

    return markets
