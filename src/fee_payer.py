from typing import List, NamedTuple, Optional, Union

import solana.system_program as sys_lib
from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment, Max, Single
from solana.rpc.types import RPCResponse
from solana.transaction import Transaction, TransactionInstruction


class UninitializedAccount(NamedTuple):
    account: PublicKey
    """Public key of an uninitialized account."""
    instruction: TransactionInstruction
    """Transaction or transaction instruction to execute to intialize the account."""


class Payer(Account):
    """An account to execute transactions and pay for fees on the Serum Dex."""

    def __init__(
        self, endpoint: str, dex_program_id: PublicKey, secret_key: Optional[Union[bytes, str, List[int], int]] = None
    ) -> None:
        """An account key pair (public and secret keys)."""
        self._conn = Client(endpoint)
        self._dex = dex_program_id
        super().__init__(secret_key)

    def create_program_account(
        self, program_id: PublicKey, space: int, new_account: Optional[PublicKey] = None
    ) -> UninitializedAccount:
        """Create an unitialized account for a specific program."""
        if not new_account:
            new_account = Account().public_key()
        mbfre_resp = self._conn.get_minimum_balance_for_rent_exemption(usize=space, commitment=Single)
        create_account_params = sys_lib.CreateAccountParams(
            from_pubkey=self.public_key(),
            new_account_pubkey=new_account,
            lamports=mbfre_resp["result"],
            space=space,
            program_id=program_id,
        )  # TODO: Bump solana and only add param.
        return UninitializedAccount(new_account, sys_lib.create_account(create_account_params).instructions[0])

    def create_dex_account(self, unpadded_len: int, new_account: Optional[PublicKey] = None) -> UninitializedAccount:
        """Create an unitialized account for the dex program."""
        if not new_account:
            new_account = Account().public_key()
        return self.create_program_account(self._dex, unpadded_len + 12, new_account)

    @staticmethod
    def build_transaction(*instructions: TransactionInstruction) -> Transaction:
        """Build transaction from the provided instructions"""
        return Transaction().add(*instructions)

    def sign_transaction(self, txn: Transaction) -> None:
        """Sign transaction with the payer account."""
        txn.sign(self)

    def send_transaction(
        self,
        txn: Transaction,
        *additional_signers: Account,
        signed: bool = False,
        skip_preflight: bool = False,
        preflight_commitment: Commitment = Max
    ) -> RPCResponse:
        """Send (broadcast) the transaction to the network."""
        return (
            self._conn.send_raw_transaction(txn, preflight_commitment=preflight_commitment)
            if signed
            else self._conn.send_transaction(
                txn, self, *additional_signers, skip_preflight=skip_preflight, preflight_commitment=preflight_commitment
            )
        )
