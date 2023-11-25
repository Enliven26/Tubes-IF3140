from abc import ABC, abstractmethod
from typing import List, Type, TypeVar
from cores.Transaction import Transaction
from cores.InstructionReader import InstructionReader
from cores.ResourceManager import ResourceManager

Reader = TypeVar('Reader', bound=InstructionReader)

class Transaction(ABC):
    # Your Transaction class definition here
    pass

class TransactionManager(ABC):
    def __init__(self, instruction_reader: Reader) -> None:
        super().__init__()

        self.__resource_manager: ResourceManager = ResourceManager()
        self.__instruction_reader: Reader = instruction_reader

    def _get_resource_manager(self):
        return self.__resource_manager
    
    def _get_instruction_reader(self):
        return self.__instruction_reader

    @abstractmethod
    def get_next_instruction(self):
        pass

    @abstractmethod
    def abort(self, transaction_id: str):
        pass

    @abstractmethod
    def wait(self, transaction_id: str):
        pass