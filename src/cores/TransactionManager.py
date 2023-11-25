from abc import ABC, abstractmethod
from typing import TypeVar
from cores.InstructionReader import InstructionReader
from cores.ResourceManager import ResourceManager
from cores.Instruction import Instruction

Reader = TypeVar('Reader', bound=InstructionReader)

class TransactionManager(ABC):
    def __init__(self, instruction_reader: Reader) -> None:
        super().__init__()

        self.__resource_manager: ResourceManager = ResourceManager()
        self.__instruction_reader: Reader = instruction_reader

    def _console_log(self, *args):
        formatted_message = "[TRANSACTION MANAGER] " + ' '.join(map(str, args))
        print(formatted_message)

    def _get_resource_manager(self):
        return self.__resource_manager
    
    def _get_next_instruction(self) -> Instruction:
        return self.__instruction_reader.get_next_instruction()
    
    @abstractmethod
    def __process_instruction(self, instruction: Instruction):
        pass

    @abstractmethod
    def __process_after_instruction(self):
        pass

    @abstractmethod
    def _abort(self, transaction_id: str):
        pass

    @abstractmethod
    def _print_all_transactions_status(self):
        pass

    def run(self):
        while True:
            try:
                instruction = self.__instruction_reader.get_next_instruction()
                self.__process_instruction(instruction)
                self.__process_after_instruction()
            
            except EOFError:
                self._console_log("No more instruction received")
                self._print_all_transactions_status()
                break

