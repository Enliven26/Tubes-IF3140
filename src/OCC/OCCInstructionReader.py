from cores.InstructionReader import InstructionReader, InstructionLine, InstructionType
from cores.Instruction import Instruction
from OCC.instructions import OCCReadInstruction, OCCWriteInstruction, OCCCommitInstruction
from cores.exceptions import InvalidInstructionLineException
from OCC.OCCResourceHandler import OCCResourceHandler

class OCCInstructionReader(InstructionReader):
    def __init__(self, file_path: str, resource_handler: OCCResourceHandler) -> None:
        super().__init__(file_path)
        self.__resource_handler = resource_handler

    def _get_instruction_from_line(self, instruction_line: InstructionLine) -> Instruction:
        type = instruction_line.instruction_type

        if (type == InstructionType.R):
            return OCCReadInstruction(
                instruction_line.transaction_id,
                self.__resource_handler,
                instruction_line.resource_id,
            )

        elif (type == InstructionType.W):
            return OCCWriteInstruction(
                instruction_line.transaction_id,
                self.__resource_handler,
                instruction_line.resource_id,
                instruction_line.update_value
            )

        elif (type == InstructionType.C):
            return OCCCommitInstruction(
                instruction_line.transaction_id,
                self.__resource_handler
            )

        raise InvalidInstructionLineException()