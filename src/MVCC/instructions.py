from cores.Instruction import Instruction
from MVCC.VersionController import VersionController
from cores.Instruction import InstructionType
from MVCC.MVCCTransaction import MVCCTransactionContainer
    
class MVCCInstruction(Instruction):
    def __init__(self, transaction_id: str, version_controller: VersionController) -> None:
        super().__init__(transaction_id)
        self.__version_controller = version_controller

    def _get_version_controller(self) -> VersionController:
        return self.__version_controller
    
class MVCCAccessInstruction(MVCCInstruction):
    def __init__(
            self,
            transaction_id: str,
            version_controller: VersionController, 
            resource_id: str
        ) -> None:

        super().__init__(transaction_id, version_controller)
        self.__resource_id = resource_id
    
    def _get_resource_id(self) -> str:
        return self.__resource_id
    
    def _get_transaction_container(self, **kwargs) -> MVCCTransactionContainer:
        return kwargs.get('transaction_container')
    
class MVCCWriteInstruction(MVCCAccessInstruction):
    def __init__(
            self, 
            transaction_id: str,
            version_controller: VersionController, 
            resource_id: str, 
            update_value: int) -> None:
        
        super().__init__(transaction_id, version_controller, resource_id)
        self.__update_value = update_value
    
    def get_transaction_type(self) -> InstructionType:
        return InstructionType.W
    
    def __str__(self) -> str:
        return f"W({self._get_resource_id()}={self.__update_value}) from transaction {self.get_transaction_id()}"

    def execute(self, **kwargs):
        transaction_id = self.get_transaction_id()
        resource_id = self._get_resource_id()
        transaction_timestamp = self._get_transaction_container(**kwargs).get_timestamp()
        version_controller = self._get_version_controller()

        self._console_log("[ Transaction", transaction_id, "is writing on resource", resource_id, "]")

        version_controller.write(resource_id, transaction_id, transaction_timestamp, self.__update_value)

    
class MVCCReadInstruction(MVCCAccessInstruction):
    def __init__(
            self, 
            transaction_container: MVCCTransactionContainer,
            version_controller: VersionController, 
            resource_id: str
        ) -> None:

        super().__init__(transaction_container, version_controller, resource_id)
    
    def get_transaction_type(self) -> InstructionType:
        return InstructionType.R
    
    def __str__(self) -> str:
        return f"R({self._get_resource_id()}) from transaction {self.get_transaction_id()}"

    def execute(self, **kwargs):
        transaction_id = self.get_transaction_id()
        resource_id = self._get_resource_id()
        transaction_timestamp = self._get_transaction_container(**kwargs).get_timestamp()
        version_controller = self._get_version_controller()

        self._console_log("[ Transaction", transaction_id, "is reading on resource", resource_id, "]")
        version_controller.read(resource_id, transaction_id, transaction_timestamp)

class MVCCCommitInstruction(MVCCInstruction):
    def __init__(
            self, 
            transaction_id: str,
            version_controller: VersionController, 
        ) -> None:

        super().__init__(transaction_id, version_controller)

    def get_transaction_type(self) -> InstructionType:
        return InstructionType.C

    def __str__(self) -> str:
        return f"commit from transaction {self.get_transaction_id()}"
    
    def execute(self, **kwargs):
        transaction_id = self.get_transaction_id()
        self._get_version_controller().commit(transaction_id)
        self._console_log("Transaction", transaction_id, "committed")