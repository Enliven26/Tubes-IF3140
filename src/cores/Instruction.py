from abc import ABC, abstractmethod
from enum import Enum
from cores.LogWriter import LogWriter

class InstructionType(Enum):
    R = "READ"
    W = "WRITE"
    C = "COMMIT"

class Instruction(ABC):

    def __init__(self, transaction_id: str) -> None:
        super().__init__()
        self.__transaction_id = transaction_id
        self.__log_writer = LogWriter("INSTRUCTION")
    
    def get_transaction_id(self):
        return self.__transaction_id
    
    def _console_log(self, *args):
        # USE THIS FOR PRINTING FROM INSTRUCTION PERSPECTIVE
        self.__log_writer.console_log(*args)

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def get_transaction_type(self) -> InstructionType:
        pass

    @abstractmethod
    def execute(self, **kwargs):
        # THIS METHOD IS THE EXECUTION OF THE INSTRUCTION
        # Use kwargs if the data is impossible to be passed from init
        pass


