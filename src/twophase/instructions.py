from cores.Instruction import Instruction
from cores.ResourceManager import ResourceManager
from twophase.LockManager import LockManager
from twophase.locks import LockType

class InstructionWithLock(Instruction):
    def __init__(self, transaction_id: str, lock_manager: LockManager) -> None:
        super().__init__(transaction_id)
        self.__lock_manager = lock_manager

    def _get_lock_manager(self):
        return self.__lock_manager

class AccessInstructionWithLock(InstructionWithLock):
    def __init__(
            self,
            transaction_id: str, 
            lock_manager: LockManager, 
            resource_manager: ResourceManager, 
            resource_id: str
        ) -> None:
        
        super().__init__(transaction_id, lock_manager)
        self.__resource_manager = resource_manager
        self.__resource_id = resource_id
    
    def _get_resource_manager(self):
        return self.__resource_manager

    def _get_resource_id(self) -> str:
        return self.__resource_id
    
class WriteInstructionWithLock(AccessInstructionWithLock):
    def __init__(
            self, 
            transaction_id: str, 
            lock_manager: LockManager, 
            resource_manager: ResourceManager, 
            resource_id: str, 
            update_value: int) -> None:
        
        super().__init__(transaction_id, lock_manager, resource_manager, resource_id)
        self.__update_value = update_value

    def execute(self):
        lock_manager = self._get_lock_manager()
        transaction_id = self._get_transaction_id()
        resource_id = self._get_resource_id()
        resource_manager = self._get_resource_manager()

        if (not lock_manager.is_lock_exist(transaction_id, resource_id, LockType.EXCLUSIVE)):
            lock_manager.add_or_upgrade_to_exclusive_lock(transaction_id, resource_id)
        
        old_value = resource_manager.write(resource_id, self.__update_value)

        self._console_log("Transaction", transaction_id, "wrote resource", resource_id, "from value", old_value, "to", self.__update_value)

    
class ReadInstructionWithLock(AccessInstructionWithLock):
    def __init__(
            self, 
            transaction_id: str, 
            lock_manager: LockManager, 
            resource_manager: ResourceManager, 
            resource_id: str
        ) -> None:

        super().__init__(transaction_id, lock_manager, resource_manager, resource_id)
    
    def execute(self):
        lock_manager = self._get_lock_manager()
        transaction_id = self._get_transaction_id()
        resource_id = self._get_resource_id()
        resource_manager = self._get_resource_manager()

        if (not lock_manager.is_lock_exist(transaction_id, resource_id, LockType.SHARE)):
            lock_manager.add_share_lock(transaction_id, resource_id)
        
        value = resource_manager.read(resource_id)

        self._console_log("Transaction", transaction_id, "read resource", resource_id, "with value", value)

class CommitInstructionWithLock(InstructionWithLock):
    def __init__(
            self, 
            transaction_id: str, 
            lock_manager: LockManager
        ) -> None:

        super().__init__(transaction_id, lock_manager)

    def execute(self):
        lock_manager = self._get_lock_manager()
        transaction_id = self._get_transaction_id()

        self._console_log("Transaction", transaction_id, "committed")
        lock_manager.unlockAll(transaction_id)