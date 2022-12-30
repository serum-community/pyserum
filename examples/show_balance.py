
"""
Shows what is in your wallet.
"""

from pyserum.connection import conn
from solana.publickey import PublicKey
from solana.rpc.types import TokenAccountOpts
from collections import namedtuple

Token = namedtuple("Token", "name address")


def show_token_and_sol_balance(account: str, token: Token) -> None:
    """Displays the Sol balance and the balance of a token. """
    cc = conn("https://api.mainnet-beta.solana.com/")
    # get_account_info
    pub_key = PublicKey(account)

    # get_balance in SOL
    balance = cc.get_balance(pub_key)  # this matches Phantom Wallet
    print('Sol balance: {}'.format(balance.value / 1000000000))

    usdc_mint = PublicKey(token.address)
    opts = TokenAccountOpts(mint=usdc_mint)
    token_accounts = cc.get_token_accounts_by_owner(pub_key, opts)
    if len(token_accounts.value) > 1:
        print(f'more than one token account for: {token.name}')
        return

    # parse out the public key
    token_account_address = token_accounts.value[0].pubkey
    # this should be stored in a more involved program to avoid extra RPC calls

    # token balances are stored in token accounts, not in the main wallet like SOL,
    # you need to get the token account address from the above get_token_accounts_by_owner call
    token_balance = cc.get_token_account_balance(PublicKey(token_account_address))
    print(f"{token.name}: {token_balance.value.ui_amount_string}")


if __name__ == '__main__':

    # some_address = "7VHUFJHWu2CuExkJcJrzhQPJ2oygupTWkL2A2For4BmE"
    some_address = "HjHSNe8hhvZ8hKCRrhKg1DGiGPd9NYQbUjT1SQRDo4kZ"
    usdc = Token("USDC", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

    show_token_and_sol_balance(some_address, usdc)

