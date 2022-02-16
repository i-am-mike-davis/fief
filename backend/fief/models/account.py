from typing import TYPE_CHECKING, List, Optional, Union

from sqlalchemy import Column, Enum, String, Text, engine, event
from sqlalchemy.orm import relationship

from fief.crypto.encryption import decrypt, encrypt
from fief.db.types import DatabaseType, get_driver
from fief.models.base import GlobalBase
from fief.models.generics import CreatedUpdatedAt, UUIDModel
from fief.settings import settings

if TYPE_CHECKING:
    from fief.models.account_user import AccountUser


class Account(UUIDModel, CreatedUpdatedAt, GlobalBase):
    __tablename__ = "accounts"

    name: str = Column(String(length=255), nullable=False)
    domain: str = Column(String(length=255), nullable=False)

    database_type: Optional[DatabaseType] = Column(Enum(DatabaseType), nullable=True)
    database_host: Optional[str] = Column(Text, nullable=True)
    database_port: Optional[str] = Column(Text, nullable=True)
    database_username: Optional[str] = Column(Text, nullable=True)
    database_password: Optional[str] = Column(Text, nullable=True)
    database_name: Optional[str] = Column(Text, nullable=True)

    account_users: List["AccountUser"] = relationship(
        "AccountUser", back_populates="account"
    )

    def __repr__(self) -> str:
        return f"Account(id={self.id}, name={self.name}, domain={self.domain})"

    def get_database_url(self, asyncio=True) -> engine.URL:
        """
        Return the database URL for this account.

        If it's not specified on the model, the instance database URL is returned.
        """
        if self.database_type is None:
            url = settings.get_database_url(asyncio)
        else:
            url = engine.URL.create(
                drivername=get_driver(self.database_type, asyncio=asyncio),
                username=self._decrypt_database_setting("database_username"),
                password=self._decrypt_database_setting("database_password"),
                host=self._decrypt_database_setting("database_host"),
                port=self._decrypt_database_port(),
                database=self._decrypt_database_setting("database_name"),
            )

        dialect_name = url.get_dialect().name
        if dialect_name == "sqlite":
            url = url.set(database=f"{self.get_schema_name()}.db")

        return url

    def get_schema_name(self) -> str:
        """
        Return the SQL schema name where the data is stored.
        """
        return str(self.id)

    def _decrypt_database_setting(self, attribute: str) -> Optional[str]:
        value = getattr(self, attribute)
        if value is None:
            return value
        return decrypt(value, settings.encryption_key)

    def _decrypt_database_port(self) -> Optional[int]:
        value = self._decrypt_database_setting("database_port")
        if value is None:
            return value
        return int(value)


def encrypt_database_setting(
    target: Account,
    value: Optional[Union[str, int]],
    oldvalue: Optional[str],
    initiator,
):
    if value is None:
        return value
    return encrypt(str(value), settings.encryption_key)


event.listen(Account.database_host, "set", encrypt_database_setting, retval=True)
event.listen(Account.database_port, "set", encrypt_database_setting, retval=True)
event.listen(Account.database_username, "set", encrypt_database_setting, retval=True)
event.listen(Account.database_password, "set", encrypt_database_setting, retval=True)
event.listen(Account.database_name, "set", encrypt_database_setting, retval=True)
