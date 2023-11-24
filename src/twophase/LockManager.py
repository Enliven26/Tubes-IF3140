from lib.Resource import Resource
from lib.Transaction import Transaction
from twophase.locks import Lock, LockType
from twophase.exceptions import LockNotFoundException, LockAlreadyExistException, LockUpgradeException, LockSharingException

class LockManager:

    def __init__(self) -> None:
        self.__resource_locks: dict[Resource, list[Lock]] = {}
        self.__transaction_locks: dict[Transaction, list[Lock]] = {}

    def __get_lock(self, transaction: Transaction, resource: Resource, type: LockType | None = None) -> Lock | None:
        locks = self.__transaction_locks[transaction]

        if (locks):
            for lock in locks:
                if (lock.get_resource() == resource and (type is None or lock.get_type() == type)):
                    return lock

        return None

    def __is_sharing_available(self, transaction: Transaction, resource: Resource) -> bool:
        locks = self.__resource_locks[resource]

        for lock in locks:
            if (lock.get_transaction() != transaction and lock.get_type() == LockType.EXCLUSIVE):
                return False

        return True

    def __is_exclusive_available(self, transaction: Transaction, resource: Resource) -> bool:
        locks = self.__resource_locks[resource]

        for lock in locks:
            if (lock.get_transaction() != transaction):
                return False

        return True

    def add_share_lock(self, transaction: Transaction, resource: Resource):
        if (self.__get_lock(transaction, resource) is not None):
            raise LockAlreadyExistException
        
        if (not self.__is_sharing_available()):
            raise LockSharingException()
        
        lock = Lock(LockType.SHARE, transaction, resource)
        self.__resource_locks[resource].append(lock)
        self.__transaction_locks[transaction].append(lock)

    def add_exclusive_lock(self, transaction: Transaction, resource: Resource):

        old_lock = self.__get_lock(transaction, resource)

        if (old_lock is not None):
            self.upgrade_lock(transaction, resource)

        else:

            if (not self.__is_exclusive_available()):
                raise LockSharingException()
                  
            lock = Lock(LockType.EXCLUSIVE, transaction, resource)
            self.__resource_locks[resource].append(lock)
            self.__transaction_locks[transaction].append(lock)

    def upgrade_lock(self, transaction: Transaction, resource: Resource):
        lock = self.__get_lock(transaction, resource)

        if (lock is None):
            raise LockNotFoundException()
        
        if (not self.__is_exclusive_available()):
            raise LockSharingException()
        
        lock.upgrade()

    def unlockAll(self, transaction: Transaction):

        locks = self.__transaction_locks[transaction]

        for lock in locks:
            self.__resource_locks[lock.get_resource()].remove(lock)

        locks.clear()

