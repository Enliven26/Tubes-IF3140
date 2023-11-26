from abc import ABC, abstractmethod
from typing import TypeVar
from cores.InstructionReader import InstructionReader
from cores.Instruction import Instruction
from cores.LogWritter import LogWriter

Reader = TypeVar('Reader', bound=InstructionReader)

class TransactionManager(ABC):
    def __init__(self, instruction_reader: Reader) -> None:
        super().__init__()

        self.__instruction_reader: Reader = instruction_reader
        self.__log_writer = LogWriter("TRANSACTION MANAGER")

    def _console_log(self, *args):
        # USE THIS FOR PRINTING FROM TRANSACTION MANAGER PERSPECTIVE
        self.__log_writer.console_log(*args)
    
    def _is_reader_closed(self) -> bool:
        return self.__instruction_reader.is_closed()
    
    def _get_next_instruction_from_file(self) -> Instruction:
        return self.__instruction_reader.get_next_instruction()
    
    @abstractmethod
    def _get_next_remaining_instruction(self) -> Instruction | None:
        # USE THIS IF NECESSARY TO GET INSTRUCTION AFTER FILE READER IS CLOSED
        pass
    
    @abstractmethod
    def _process_instruction(self, instruction: Instruction):
        # USE THIS TO PROCESS INSTRUCTION GIVEN
        pass

    @abstractmethod
    def _print_all_transactions_status(self):
        # USE THIS TO PRINT END STATUS OF ALL TRANSACTIONS AND RESOURCES
        pass

    @abstractmethod
    def _is_finish_or_stop(self) -> bool:
        # USE THIS TO DECIDE OF MANAGER STOP AFTER FILE READER IS CLOSED
        pass

    def run(self):
        # CALL THIS TO RUN TRANSACTION MANAGER
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
                    self.__log_writer.console_log_separator()
                    self.__log_writer.console_log("No more instruction received")
                    self._print_all_transactions_status()
                    break

