from cores.InstructionReader import InstructionReader, InstructionLine, InstructionType
from cores.Instruction import Instruction
from twophase.instructions import ReadInstructionWithLock, WriteInstructionWithLock, CommitInstructionWithLock
from cores.exceptions import InvalidInstructionLineException
from twophase.LockManager import LockManager
from twophase.TwoPhaseResourceHandler import TwoPhaseResourceHandler

class TwoPhaseInstructionReader(InstructionReader):
    def __init__(self, file_path: str, lock_manager: LockManager, resource_handler: TwoPhaseResourceHandler) -> None:
        super().__init__(file_path)
        self.__lock_manager = lock_manager
        self.__resource_handler = resource_handler

    def _get_instruction_from_line(self, instruction_line: InstructionLine) -> Instruction:
        type = instruction_line.instruction_type

        if (type == InstructionType.R):
            return ReadInstructionWithLock(
                instruction_line.transaction_id,
                self.__lock_manager,
                self.__resource_handler,
                instruction_line.resource_id
            )

        elif (type == InstructionType.W):
            return WriteInstructionWithLock(
                instruction_line.transaction_id,
                self.__lock_manager,
                self.__resource_handler,
                instruction_line.resource_id,
                instruction_line.update_value
            )

        elif (type == InstructionType.C):
            return CommitInstructionWithLock(
                instruction_line.transaction_id,
                self.__lock_manager
            )

        raise InvalidInstructionLineException()