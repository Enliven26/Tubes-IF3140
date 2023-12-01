from cores.Instruction import Instruction
from OCC.OCCResourceHandler import OCCResourceHandler
from cores.Instruction import InstructionType
from OCC.OCCTransaction import OCCTransactionContainer
    
class OCCInstruction(Instruction):
    def __init__(self, transaction_id: str, resource_handler: OCCResourceHandler) -> None:
        super().__init__(transaction_id)
        self.__resource_handler = resource_handler

    def _get_resource_handler(self) -> OCCResourceHandler:
        return self.__resource_handler
    
class OCCAccessTransaction(OCCInstruction):
    def __init__(
            self,
            transaction_id: str,
            resource_handler: OCCResourceHandler, 
            resource_id: str
        ) -> None:

        super().__init__(transaction_id, resource_handler)
        self.__resource_id = resource_id
    
    def _get_resource_id(self) -> str:
        return self.__resource_id
    
    def _get_transaction_container(self, **kwargs) -> OCCTransactionContainer:
        return kwargs.get('transaction_container')
    
class OCCWriteInstruction(OCCAccessTransaction):
    def __init__(self, transaction_id: str, resource_handler: OCCResourceHandler, resource_id: str, update_value: int) -> None:
        super().__init__(transaction_id, resource_handler, resource_id)
        self.__update_value = update_value
    
    def get_transaction_type(self) -> InstructionType:
        return InstructionType.W
    
    def __str__(self) -> str:
        return f"W({self._get_resource_id()}={self.__update_value}) from transaction {self.get_transaction_id()}"

    def execute(self, **kwargs):
        transaction_id = self.get_transaction_id()
        resource_handler = self._get_resource_handler()
        resource_id = self._get_resource_id()
        transaction_container = self._get_transaction_container(**kwargs)

        old_value = resource_handler.write(transaction_container, resource_id, self.__update_value)

        self._console_log(
            "Transaction", 
            transaction_id, 
            "wrote snapshot of resource", 
            resource_id, 
            "from", 
            old_value,
            "to",
            self.__update_value
        )

    
class OCCReadInstruction(OCCAccessTransaction):
    def __init__(self, transaction_id: str, resource_handler: OCCResourceHandler, resource_id: str) -> None:
        super().__init__(transaction_id, resource_handler, resource_id)
    
    def get_transaction_type(self) -> InstructionType:
        return InstructionType.R
    
    def __str__(self) -> str:
        return f"R({self._get_resource_id()}) from transaction {self.get_transaction_id()}"

    def execute(self, **kwargs):
        transaction_id = self.get_transaction_id()
        resource_handler = self._get_resource_handler()
        resource_id = self._get_resource_id()
        transaction_container = self._get_transaction_container(**kwargs)

        value = resource_handler.read(transaction_container, resource_id)

        self._console_log("Transaction", transaction_id, "read snapshot of resource", resource_id, "with value", value)

class OCCCommitInstruction(OCCInstruction):
    def __init__(self, transaction_id: str, resource_handler: OCCResourceHandler) -> None:
        super().__init__(transaction_id, resource_handler)

    def get_transaction_type(self) -> InstructionType:
        return InstructionType.C

    def __str__(self) -> str:
        return f"commit from transaction {self.get_transaction_id()}"
    
    def execute(self, **kwargs):
        transaction_id = self.get_transaction_id()
        self._get_resource_handler().commit(transaction_id)
        self._console_log("Transaction", transaction_id, "committed")