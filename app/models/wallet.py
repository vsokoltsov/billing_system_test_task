from decimal import Decimal, InvalidOperation

import sqlalchemy as sa
from databases.backends.postgres import Record

from app.db import db, metadata
from app.models.wallet_operations import WalletOperation

wallets = sa.Table(
    "wallets",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, nullable=False),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="cascade"),
        nullable=False,
        unique=True,
    ),
    sa.Column(
        "balance", sa.Numeric(10, 2, asdecimal=True), nullable=False, server_default="0"
    ),
)


class InsufficientFundsException(Exception):
    """ Insufficient funds exception. """


class Wallet:
    """ Represents operations with wallet. """

    @classmethod
    async def create(cls, user_id: int) -> Record:
        """
        Creates new wallet instance.

        :params user_id: ID of user
        :returns: SQL row record
        """

        wallet_query = wallets.insert(None).values({"user_id": user_id})
        await WalletOperation.create(WalletOperation.CREATE)
        return await db.execute(wallet_query)

    @classmethod
    async def enroll(cls, wallet_id: int, amount: Decimal) -> Decimal:
        """
        Put amount of money to the wallet.

        :param wallet_id: ID of walled
        :param amount: Number that need to be applied for wallet's balance.
        :returns: Balance decimal value
        """

        try:
            Decimal(amount)
        except InvalidOperation as wrong_type:
            raise ValueError("Wrong type of 'amount' field") from wrong_type

        assert amount > 0, "amount should be positive"

        async with db.transaction():
            query = (
                wallets.update(None)
                .where(wallets.c.id == wallet_id)
                .values({"balance": wallets.c.balance + amount})
                .returning(wallets.c.balance)
            )
            balance = await db.execute(query)
            await WalletOperation.create(
                WalletOperation.RECEIPT,
                amount,
                wallet_to=wallet_id,
            )
            return balance

    @classmethod
    async def get_by_user_id(cls, user_id: int) -> Record:
        """
        Retrieve wallet row record by user_id value.

        :param user_id: ID of user:
        :returns: SQL row record
        """

        wallet_query = wallets.select().where(wallets.c.user_id == user_id)
        return await db.fetch_one(wallet_query)

    @classmethod
    async def transfer(cls, wallet_from: int, wallet_to: int, amount: Decimal) -> int:
        """
        Transfer amount of currency between wallets.

        :param wallet_from: ID of source wallet
        :param wallet_to: ID of wallet recepients
        :param amount: Amount of currency
        :returns: Source wallet id
        """

        assert amount > 0, "amount must be positive"
        assert wallet_from != wallet_to, "wallet source and target must be different"

        async with db.transaction():
            # Get source wallet data
            get_source_query = wallets.select().where(wallets.c.id == wallet_from)
            source_wallet = await db.fetch_one(get_source_query)
            if source_wallet.get("balance") < amount:
                raise InsufficientFundsException(
                    "Source wallet does not have enough funcds."
                )

            # Update wallets information for both source and target
            source_query = (
                wallets.update(None)
                .where(wallets.c.id == wallet_from)
                .values({"balance": wallets.c.balance - amount})
            )
            target_query = (
                wallets.update(None)
                .where(wallets.c.id == wallet_to)
                .values({"balance": wallets.c.balance + amount})
            )
            await db.execute(source_query)
            await db.execute(target_query)

            await WalletOperation.create(
                WalletOperation.DEBIT,
                amount,
                wallet_from=wallet_from,
                wallet_to=wallet_to,
            )
            await WalletOperation.create(
                WalletOperation.RECEIPT,
                amount,
                wallet_from=wallet_to,
                wallet_to=wallet_from,
            )

            return wallet_from
