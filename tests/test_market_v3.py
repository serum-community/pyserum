from solana.rpc.api import Client
from pyserum.market import Market
from solana.publickey import PublicKey

http_client = Client("https://api.mainnet-beta.solana.com/")
stubbed_market_pk = PublicKey("teE55QrL4a4QSfydR9dnHF97jgCfptpuigbb53Lo95g")
stubbed_dex_program_pk = PublicKey("9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin")
market = Market.load(http_client, stubbed_market_pk, stubbed_dex_program_pk, force_use_request_queue=True)



