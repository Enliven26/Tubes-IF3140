from enum import Enum
from twophase.exceptions import LockUpgradeException

class LockType(Enum):
    SHARE: 0
    EXCLUSIVE: 1

class Lock:
    def __init__(self, type: LockType, transaction_id: str, resource_id: str) -> None:
        self.__type = type
        self.__transaction_id = transaction_id
        self.__resourc_id = resource_id

    def get_type(self) -> LockType:
        return self.__type
    
    def get_transaction_id(self) -> str:
        return self.__transaction_id
    
    def get_resource_id(self) -> str:
        return self.__resourc_id
    
    def upgrade(self):
        if (self.__type != LockType.SHARE):
            raise LockUpgradeException()
        
        self.__type = LockType.EXCLUSIVE