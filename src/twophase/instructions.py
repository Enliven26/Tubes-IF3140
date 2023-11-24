from lib.Instruction import Instruction
from lib.Resource import Resource
from lib.ResourceManager import ResourceManager
from twophase.LockManager import LockManager

class InstructionWithLock(Instruction):
    def __init__(self, resource_manager: ResourceManager, lock_manager: LockManager) -> None:
        super().__init__(resource_manager)
        self.__lock_manager = lock_manager

    def _get_lock_manager(self):
        return self.__lock_manager

class AccessInstructionWithLock(InstructionWithLock):
    def __init__(self, resource_manager: ResourceManager, lock_manager: LockManager, resource: Resource) -> None:
        super().__init__(resource_manager, lock_manager)
        self.__resource = resource

    def _get_resource(self) -> Resource:
        return self.__resource
    
class WriteInstructionWithLock(AccessInstructionWithLock):
    def __init__(
            self, 
            resource_manager: 
            ResourceManager, 
            lock_manager: LockManager, 
            resource: Resource, 
            update_value: int) -> None:
        
        super().__init__(resource_manager, lock_manager, resource)
        self.__update_value = update_value

    def execute(self):
        
    
class ReadInstructionWithLock(AccessInstructionWithLock):
    def __init__(self, resource_manager: ResourceManager, lock_manager: LockManager, resource: Resource) -> None:
        super().__init__(resource_manager, lock_manager, resource)
    
    def execute(self):
        return super().execute()

class CommitInstructionWithLock(InstructionWithLock):
    def __init__(self, resource_manager: ResourceManager, lock_manager: LockManager) -> None:
        super().__init__(resource_manager, lock_manager)

    def execute(self):
        return super().execute()