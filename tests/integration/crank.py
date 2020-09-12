import spl.token.instructions as token_instructions
from solana.account import Account
from solana.rpc.types import RPCResponse
from solana.transaction import Transaction
from spl.token.constants import MINT_LEN, TOKEN_PROGRAM_ID

from src.payer import Payer


def genesis(payer: Payer, mint: Account, decimals: int) -> RPCResponse:
    """The genesis crank event."""
    init_mint_account = payer.create_program_account(TOKEN_PROGRAM_ID, MINT_LEN, mint.public_key())
    init_mint_instruction = token_instructions.initialize_mint(
        token_instructions.InitializeMintParams(
            decimals=decimals, program_id=TOKEN_PROGRAM_ID, mint=mint.public_key(), mint_authority=payer.public_key()
        )
    )

    txn = Transaction()
    txn.add(init_mint_account.instruction)
    txn.add(init_mint_instruction)

    return payer.send_transaction(txn, mint, skip_preflight=True)
