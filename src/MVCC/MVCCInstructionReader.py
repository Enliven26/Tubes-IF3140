from cores.InstructionReader import InstructionReader, InstructionLine, InstructionType
from cores.Instruction import Instruction
from MVCC.instructions import MVCCReadInstruction, MVCCWriteInstruction, MVCCCommitInstruction
from cores.exceptions import InvalidInstructionLineException
from MVCC.VersionController import VersionController

class MVCCInstructionReader(InstructionReader):
    def __init__(self, file_path: str, version_controller: VersionController) -> None:
        super().__init__(file_path)
        self.__version_controller = version_controller

    def _get_instruction_from_line(self, instruction_line: InstructionLine) -> Instruction:
        type = instruction_line.instruction_type

        if (type == InstructionType.R):
            return MVCCReadInstruction(
                instruction_line.transaction_id,
                self.__version_controller,
                instruction_line.resource_id
            )

        elif (type == InstructionType.W):
            return MVCCWriteInstruction(
                instruction_line.transaction_id,
                self.__version_controller,
                instruction_line.resource_id,
                instruction_line.update_value
            )

        elif (type == InstructionType.C):
            return MVCCCommitInstruction(
                instruction_line.transaction_id,
                self.__version_controller
            )

        raise InvalidInstructionLineException()