from abc import ABC, abstractmethod
from enum import Enum

class InstructionType(Enum):
    R = "READ"
    W = "WRITE"
    C = "COMMIT"

class Instruction(ABC):

    def __init__(self, transaction_id: str) -> None:
        super().__init__()
        self.__transaction_id = transaction_id
    
    def get_transaction_id(self):
        return self.__transaction_id
    
    def _console_log(self, *args):
        formatted_message = "[INSTRUCTION] " + ' '.join(map(str, args))
        print(formatted_message)

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def get_transaction_type(self) -> InstructionType:
        pass

    @abstractmethod
    def execute(self):
        pass


