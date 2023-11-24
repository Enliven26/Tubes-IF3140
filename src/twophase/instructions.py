from lib.Instruction import Instruction
from lib.ResourceManager import ResourceManager
from twophase.LockManager import LockManager

class InstructionWithLock(Instruction):
    def __init__(self, transaction_id: str, resource_manager: ResourceManager, lock_manager: LockManager) -> None:
        super().__init__(transaction_id, resource_manager)
        self.__lock_manager = lock_manager

    def _get_lock_manager(self):
        return self.__lock_manager

class AccessInstructionWithLock(InstructionWithLock):
    def __init__(
            self,
            transaction_id: str, 
            resource_manager: ResourceManager, 
            lock_manager: LockManager, 
            resource_id: str
        ) -> None:
        
        super().__init__(transaction_id, resource_manager, lock_manager)
        self.__resource_id = resource_id

    def _get_resource_id(self) -> str:
        return self.__resource_id
    
class WriteInstructionWithLock(AccessInstructionWithLock):
    def __init__(
            self, 
            transaction_id: str, 
            resource_manager: ResourceManager, 
            lock_manager: LockManager, 
            resource_id: str, 
            update_value: int) -> None:
        
        super().__init__(transaction_id, resource_manager, lock_manager, resource_id)
        self.__update_value = update_value

    def execute(self):
        lock_manager = self._get_lock_manager()
        transaction = self._get_transaction_id()
        resource = self._get_resource_id()

        lock_manager.add_or_upgrade_to_exclusive_lock(transaction, resource)
    
class ReadInstructionWithLock(AccessInstructionWithLock):
    def __init__(
            self, 
            transaction_id: str, 
            resource_manager: ResourceManager, 
            lock_manager: LockManager, 
            resource_id: str
        ) -> None:

        super().__init__(transaction_id, resource_manager, lock_manager, resource_id)
    
    def execute(self):
        return super().execute()

class CommitInstructionWithLock(InstructionWithLock):
    def __init__(
            self, 
            transaction_id: str, 
            resource_manager: ResourceManager, 
            lock_manager: LockManager
        ) -> None:

        super().__init__(transaction_id, resource_manager, lock_manager)

    def execute(self):
        return super().execute()