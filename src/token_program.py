"""Token instructions."""
from typing import List, Optional

from solana.instruction import InstructionLayout, encode_data
from solana.publickey import PublicKey
from solana.sysvar import SYSVAR_RENT_PUBKEY
from solana.transaction import AccountMeta, TransactionInstruction

TOKEN_PROGRAM_ID = PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
WRAPPED_SOL_MINT = PublicKey("So11111111111111111111111111111111111111111")

# Instruction Indices
_EMPTY, _EMPTY_FMT = -1, ""
_INITIALIZE_MINT_IDX = 0
_INITIALIZE_ACCOUNT = 1
_TRANSFER = 3
_MINT_TO = 7
_BURN = 8

TOKEN_INSTRUCTION_LAYOUTS = [
    InstructionLayout(idx=_INITIALIZE_MINT_IDX, fmt="B32sB32s"),
    InstructionLayout(idx=_INITIALIZE_ACCOUNT, fmt=_EMPTY_FMT),
    InstructionLayout(idx=_EMPTY, fmt=_EMPTY_FMT),
    InstructionLayout(idx=_TRANSFER, fmt="Q"),
    InstructionLayout(idx=_EMPTY, fmt=_EMPTY_FMT),
    InstructionLayout(idx=_EMPTY, fmt=_EMPTY_FMT),
    InstructionLayout(idx=_EMPTY, fmt=_EMPTY_FMT),
    InstructionLayout(idx=_MINT_TO, fmt="Q"),
    InstructionLayout(idx=_BURN, fmt="Q"),
]


def initialize_mint(
    mint: PublicKey, decimals: int, mint_authority: PublicKey, freeze_authority: Optional[PublicKey] = None
) -> TransactionInstruction:
    """Initialize mint."""
    keys: List[AccountMeta] = [
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
    ]
    freeze_authority, freeze_authority_opt = (freeze_authority, True) if freeze_authority else (PublicKey(0), False)
    return TransactionInstruction(
        keys=keys,
        data=encode_data(
            TOKEN_INSTRUCTION_LAYOUTS[_INITIALIZE_MINT_IDX],
            decimals,
            mint_authority,
            int(freeze_authority_opt),
            freeze_authority,
        ),
        program_id=TOKEN_PROGRAM_ID,
    )


def initialize_account(account: PublicKey, mint: PublicKey, owner: PublicKey) -> TransactionInstruction:
    """Initialize token account."""
    keys: List[AccountMeta] = [
        AccountMeta(pubkey=account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=owner, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
    ]
    return TransactionInstruction(
        keys=keys, data=encode_data(TOKEN_INSTRUCTION_LAYOUTS[_INITIALIZE_ACCOUNT]), program_id=TOKEN_PROGRAM_ID
    )


def transfer(source: PublicKey, destination: PublicKey, owner: PublicKey, amount: int) -> TransactionInstruction:
    """Transfer tokens from source address to destination address."""
    keys: List[AccountMeta] = [
        AccountMeta(pubkey=source, is_signer=False, is_writable=True),
        AccountMeta(pubkey=destination, is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner, is_signer=True, is_writable=False),
    ]
    return TransactionInstruction(
        keys=keys, data=encode_data(TOKEN_INSTRUCTION_LAYOUTS[_TRANSFER], amount), program_id=TOKEN_PROGRAM_ID
    )


def approve(source: PublicKey, delegate: PublicKey, owner: PublicKey, amount: int):
    """Approve delegate address to spend token."""
    raise NotImplementedError("approve not implemented")


def mint_to(mint: PublicKey, destination: PublicKey, mint_authority: PublicKey, amount: int) -> TransactionInstruction:
    """Mint token to destination address."""
    keys: List[AccountMeta] = [
        AccountMeta(pubkey=mint, is_signer=False, is_writable=True),
        AccountMeta(pubkey=destination, is_signer=False, is_writable=True),
        AccountMeta(pubkey=mint_authority, is_signer=True, is_writable=False),
    ]
    return TransactionInstruction(
        keys=keys, data=encode_data(TOKEN_INSTRUCTION_LAYOUTS[_MINT_TO], amount), program_id=TOKEN_PROGRAM_ID
    )
