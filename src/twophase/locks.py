from enum import Enum
from lib.Transaction import Transaction
from lib.Resource import Resource
from twophase.exceptions import LockUpgradeException

class LockType(Enum):
    SHARE: 0
    EXCLUSIVE: 1

class Lock:
    def __init__(self, type: LockType, transaction: Transaction, resource: Resource) -> None:
        self.__type = type
        self.__transaction = transaction
        self.__resource = resource

    def get_type(self) -> LockType:
        return self.__type
    
    def get_transaction(self) -> Transaction:
        return self.__transaction
    
    def get_resource(self) -> Resource:
        return self.__resource
    
    def upgrade(self):
        if (self.__type != LockType.SHARE):
            raise LockUpgradeException()
        
        self.__type = LockType.EXCLUSIVE