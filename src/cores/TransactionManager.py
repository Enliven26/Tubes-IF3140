from abc import ABC, abstractmethod
from typing import TypeVar
from cores.InstructionReader import InstructionReader
from cores.ResourceManager import ResourceManager
from cores.Instruction import Instruction
from cores.LogWritter import LogWriter

Reader = TypeVar('Reader', bound=InstructionReader)

class TransactionManager(ABC):
    def __init__(self, resource_manager: ResourceManager, instruction_reader: Reader) -> None:
        super().__init__()

        self.__resource_manager: ResourceManager = resource_manager
        self.__instruction_reader: Reader = instruction_reader
        self.__log_writer = LogWriter("TRANSACTION MANAGER")

    def _console_log(self, *args):
        self.__log_writer.console_log(*args)
        
    def _get_resource_manager(self):
        return self.__resource_manager
    
    def _is_reader_closed(self) -> bool:
        return self.__instruction_reader.is_closed()
    
    def _get_next_instruction_from_file(self) -> Instruction:
        return self.__instruction_reader.get_next_instruction()
    
    @abstractmethod
    def _get_next_remaining_instruction(self) -> Instruction | None:
        pass
    
    @abstractmethod
    def _process_instruction(self, instruction: Instruction):
        pass

    @abstractmethod
    def _print_all_transactions_status(self):
        pass

    @abstractmethod
    def _is_finish_or_stop(self) -> bool:
        pass

    def run(self):
        while True:
            try:
                instruction = None

                if (not self._is_reader_closed()):
                    instruction = self._get_next_instruction_from_file()
                    
                else:
                    instruction = self._get_next_remaining_instruction()
                    if (instruction is None):
                        break

                self._process_instruction(instruction)
            
            except EOFError:
                self.__instruction_reader.close()

                if (self._is_finish_or_stop()):
                    self.__log_writer.console_log("No more instruction received")
                    self._print_all_transactions_status()
                    break

