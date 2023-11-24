
from twophase.locks import Lock, LockType
from twophase.exceptions import LockNotFoundException, LockAlreadyExistException, LockUpgradeException, LockSharingException

class LockManager:

    def __init__(self) -> None:
        self.__resource_locks: dict[str, list[Lock]] = {}
        self.__transaction_locks: dict[str, list[Lock]] = {}

    def __initialize_list_if_not_exist(self, transaction_id: str, resource_id: str):
        if self.__resource_locks.get(resource_id) is None:
            self.__resource_locks[resource_id] = []
        
        if self.__transaction_locks.get(transaction_id) is None:
            self.__transaction_locks[transaction_id] = []

    def __get_lock(self, transaction_id: str, resource_id: str, type: LockType | None = None) -> Lock | None:
        locks = self.__transaction_locks.get(transaction_id)

        if (locks is not None):
            for lock in locks:
                if (lock.get_resource_id() == resource_id and (type is None or lock.get_type() == type)):
                    return lock

        return None

    def __is_sharing_available(self, transaction_id: str, resource_id: str) -> bool:
        locks = self.__resource_locks.get(resource_id)

        if (locks is not None):
            for lock in locks:
                if (lock.get_transaction_id() != transaction_id and lock.get_type() == LockType.EXCLUSIVE):
                    return False

        return True

    def __is_exclusive_available(self, transaction_id: str, resource_id: str) -> bool:
        locks = self.__resource_locks.get(resource_id)

        if (locks is not None):
            for lock in locks:
                if (lock.get_transaction_id() != transaction_id):
                    return False

        return True

    def add_share_lock(self, transaction_id: str, resource_id: str):
        if (self.__get_lock(transaction_id, resource_id) is not None):
            raise LockAlreadyExistException
        
        if (not self.__is_sharing_available()):
            raise LockSharingException()
        
        lock = Lock(LockType.SHARE, transaction_id, resource_id)

        self.__initialize_list_if_not_exist(transaction_id, resource_id)
        
        self.__resource_locks[resource_id].append(lock)
        self.__transaction_locks[transaction_id].append(lock)

    def __upgrade_lock(self, transaction_id: str, resource_id: str):
        lock = self.__get_lock(transaction_id, resource_id)

        if (lock is None):
            raise LockNotFoundException()
        
        if (not self.__is_exclusive_available()):
            raise LockSharingException()
        
        lock.upgrade()

    def add_or_upgrade_to_exclusive_lock(self, transaction_id: str, resource_id: str):

        old_lock = self.__get_lock(transaction_id, resource_id)

        if (old_lock is not None):
            self.__upgrade_lock(transaction_id, resource_id)

        else:

            if (not self.__is_exclusive_available()):
                raise LockSharingException()
                  
            lock = Lock(LockType.EXCLUSIVE, transaction_id, resource_id)

            self.__initialize_list_if_not_exist(transaction_id, resource_id)

            self.__resource_locks[resource_id].append(lock)
            self.__transaction_locks[transaction_id].append(lock)

    def unlockAll(self, transaction_id: str):

        locks = self.__transaction_locks[transaction_id]

        for lock in locks:
            self.__resource_locks[lock.get_resource_id()].remove(lock)

        locks.clear()

