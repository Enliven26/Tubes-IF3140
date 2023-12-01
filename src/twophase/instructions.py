from cores.Instruction import Instruction
from twophase.TwoPhaseResourceHandler import TwoPhaseResourceHandler
from twophase.LockManager import LockManager
from twophase.locks import LockType
from cores.Instruction import InstructionType

class InstructionWithLock(Instruction):
    def __init__(self, transaction_id: str, lock_manager: LockManager) -> None:
        super().__init__(transaction_id)
        self.__lock_manager = lock_manager

    def _get_lock_manager(self) -> LockManager:
        return self.__lock_manager

class AccessInstructionWithLock(InstructionWithLock):
    def __init__(
            self,
            transaction_id: str, 
            lock_manager: LockManager, 
            resource_handler: TwoPhaseResourceHandler, 
            resource_id: str
        ) -> None:
        
        super().__init__(transaction_id, lock_manager)
        self.__resource_handler = resource_handler
        self.__resource_id = resource_id
    
    def _get_resource_handler(self) -> TwoPhaseResourceHandler:
        return self.__resource_handler

    def _get_resource_id(self) -> str:
        return self.__resource_id
    
class WriteInstructionWithLock(AccessInstructionWithLock):
    def __init__(
            self, 
            transaction_id: str, 
            lock_manager: LockManager, 
            resource_handler: TwoPhaseResourceHandler, 
            resource_id: str, 
            update_value: int) -> None:
        
        super().__init__(transaction_id, lock_manager, resource_handler, resource_id)
        self.__update_value = update_value
    
    def get_transaction_type(self) -> InstructionType:
        return InstructionType.W
    
    def __str__(self) -> str:
        return f"W({self._get_resource_id()}={self.__update_value}) from transaction {self.get_transaction_id()}"

    def execute(self, **kwargs):
        # ACQUIRE OR UPGRADE TO EXCLUSIVE LOCK AND UPDATE THE RESOURCE
        lock_manager = self._get_lock_manager()
        transaction_id = self.get_transaction_id()
        resource_id = self._get_resource_id()
        resource_handler = self._get_resource_handler()

        if (not lock_manager.is_lock_exist(transaction_id, resource_id, LockType.EXCLUSIVE)):
            lock_manager.add_or_upgrade_to_exclusive_lock(transaction_id, resource_id)
        
        old_value = resource_handler.write(transaction_id, resource_id, self.__update_value)

        self._console_log("Transaction", transaction_id, "wrote resource", resource_id, "from value", old_value, "to", self.__update_value)

    
class ReadInstructionWithLock(AccessInstructionWithLock):
    def __init__(
            self, 
            transaction_id: str, 
            lock_manager: LockManager, 
            resource_handler: TwoPhaseResourceHandler, 
            resource_id: str
        ) -> None:

        super().__init__(transaction_id, lock_manager, resource_handler, resource_id)
    
    def get_transaction_type(self) -> InstructionType:
        return InstructionType.R
    
    def __str__(self) -> str:
        return f"R({self._get_resource_id()}) from transaction {self.get_transaction_id()}"

    def execute(self, **kwargs):
        # GET SHARE LOCK IF ANY LOCK IS NOT HOLD AND READ THE RESOURCE
        lock_manager = self._get_lock_manager()
        transaction_id = self.get_transaction_id()
        resource_id = self._get_resource_id()
        resource_handler = self._get_resource_handler()

        if (not lock_manager.is_lock_exist(transaction_id, resource_id)):
            lock_manager.add_share_lock(transaction_id, resource_id)
        
        value = resource_handler.read(resource_id)

        self._console_log("Transaction", transaction_id, "read resource", resource_id, "with value", value)

class CommitInstructionWithLock(InstructionWithLock):
    def __init__(
            self, 
            transaction_id: str, 
            lock_manager: LockManager
        ) -> None:

        super().__init__(transaction_id, lock_manager)

    def get_transaction_type(self) -> InstructionType:
        return InstructionType.C

    def __str__(self) -> str:
        return f"commit from transaction {self.get_transaction_id()}"
    
    def execute(self, **kwargs):
        # UNLOCK ALL LOCKS 
        lock_manager = self._get_lock_manager()
        transaction_id = self.get_transaction_id()

        self._console_log("Transaction", transaction_id, "committed")
        lock_manager.unlock_all(transaction_id)