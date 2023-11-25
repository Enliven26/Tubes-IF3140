from abc import ABC, abstractmethod
from cores.ResourceManager import ResourceManager

class Instruction(ABC):

    def __init__(self, transaction_id: str) -> None:
        super().__init__()
        self.__transaction_id = transaction_id
    
    def _get_transaction_id(self):
        return self.__transaction_id
    
    def _console_log(self, *args):
        formatted_message = "[INSTRUCTION] " + ' '.join(map(str, args))
        print(formatted_message)

    @abstractmethod
    def execute(self):
        pass


