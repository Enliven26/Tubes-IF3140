
from twophase.locks import Lock, LockType
from twophase.exceptions import LockNotFoundException, LockAlreadyExistException, LockUpgradeException, LockSharingException
from cores.LogWritter import LogWriter

class LockManager:

    def __init__(self) -> None:
        self.__resource_locks: dict[str, list[Lock]] = {}
        self.__transaction_locks: dict[str, list[Lock]] = {}
        self.__log_writer = LogWriter("LOCK MANAGER")

    def _console_log(self, *args):
        self.__log_writer.console_log(*args)
        
    def __initialize_list_if_not_exist(self, transaction_id: str, resource_id: str):
        if self.__resource_locks.get(resource_id) is None:
            self.__resource_locks[resource_id] = []
        
        if self.__transaction_locks.get(transaction_id) is None:
            self.__transaction_locks[transaction_id] = []

    def __get_lock(self, transaction_id: str, resource_id: str, type: LockType | None = None) -> Lock | None:
        locks = self.__transaction_locks.get(transaction_id, [])

        for lock in locks:
            if (lock.get_resource_id() == resource_id and (type is None or lock.get_type() == type)):
                return lock

        return None

    def __is_sharing_available(self, transaction_id: str, resource_id: str) -> bool:
        locks = self.__resource_locks.get(resource_id, [])

        for lock in locks:
            if (lock.get_transaction_id() != transaction_id and lock.get_type() == LockType.EXCLUSIVE):
                return False

        return True

    def __is_exclusive_available(self, transaction_id: str, resource_id: str) -> bool:
        locks = self.__resource_locks.get(resource_id, [])

        for lock in locks:
            if (lock.get_transaction_id() != transaction_id):
                return False

        return True

    def is_lock_exist(self, transaction_id: str, resource_id: str, type: LockType | None = None):
        return self.__get_lock(transaction_id, resource_id, type) is not None
    
    def add_share_lock(self, transaction_id: str, resource_id: str):
        if (self.__get_lock(transaction_id, resource_id) is not None):
            raise LockAlreadyExistException
        
        if (not self.__is_sharing_available(transaction_id, resource_id)):
            raise LockSharingException()
        
        lock = Lock(LockType.SHARE, transaction_id, resource_id)

        self.__initialize_list_if_not_exist(transaction_id, resource_id)
        
        self.__resource_locks[resource_id].append(lock)
        self.__transaction_locks[transaction_id].append(lock)

        self._console_log("Transaction", transaction_id, "acquired share-lock for resource", resource_id)

    def __upgrade_lock(self, transaction_id: str, resource_id: str):
        lock = self.__get_lock(transaction_id, resource_id)

        if (lock is None):
            raise LockNotFoundException()
        
        if (not self.__is_exclusive_available(transaction_id, resource_id)):
            raise LockSharingException()
        
        lock.upgrade()

        self._console_log("Transaction", transaction_id, "upgraded share-lock for resource", resource_id, "to exclusive-lock")

    def add_or_upgrade_to_exclusive_lock(self, transaction_id: str, resource_id: str):

        old_lock = self.__get_lock(transaction_id, resource_id)

        if (old_lock is not None):
            self.__upgrade_lock(transaction_id, resource_id)

        else:

            if (not self.__is_exclusive_available(transaction_id, resource_id)):
                raise LockSharingException()
                  
            lock = Lock(LockType.EXCLUSIVE, transaction_id, resource_id)

            self.__initialize_list_if_not_exist(transaction_id, resource_id)

            self.__resource_locks[resource_id].append(lock)
            self.__transaction_locks[transaction_id].append(lock)

            self._console_log("Transaction", transaction_id, "acquired exclusive-lock for resource", resource_id)

    def unlockAll(self, transaction_id: str):

        locks = self.__transaction_locks.pop(transaction_id, [])

        for lock in locks:
            resource_id = lock.get_resource_id()
            resource_lock_list = self.__resource_locks.get(resource_id)
            if (resource_lock_list is not None):
                self.__resource_locks[resource_id].remove(lock)
                self._console_log("Transaction", transaction_id, "unlock resource", resource_id)
                if (len(self.__resource_locks[resource_id]) == 0):
                    self.__resource_locks.pop(resource_id)


