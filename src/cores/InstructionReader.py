from abc import ABC, abstractmethod
from enum import Enum
from cores.exceptions import InvalidInstructionLineException
from cores.Instruction import Instruction

class InstructionType(Enum):
    R = 0
    W = 1
    C = 2

class InstructionLine:
    def __init__(
            self, 
            instruction_type: InstructionType, 
            transaction_id: str, 
            resource_id: str | None = None,
            update_value: int | None = None
        ) -> None:

        self.instruction_type = instruction_type
        self.transaction_id = transaction_id
        self.resource_id = resource_id
        self.update_value = update_value

class InstructionReader(ABC):
    def __init__(self, file_path: str) -> None:
        self.__file = open(file_path, 'r')

    def __parse_line(self, line: str) -> InstructionLine:
        line = line.strip()

        # Extracting information based on the format
        parts = line.split()

        if not parts:
            # Empty line
            raise InvalidInstructionLineException("Empty line found")

        instruction_type_str = parts[0].upper()
        instruction_type = InstructionType[instruction_type_str] if instruction_type_str in InstructionType.__members__ else None

        if not instruction_type:
            # Invalid instruction type
            return InvalidInstructionLineException("Invalid instruction type found")

        transaction_id = parts[1] if len(parts) > 1 else ""
        resource_id = None
        update_value = None

        if len(parts) > 2:
            if '=' in parts[2]:
                # Write instruction
                resource_id, update_value = parts[2].split('=')
                update_value = int(update_value)
            else:
                # Read instruction
                resource_id = parts[2]

        return InstructionLine(instruction_type, transaction_id, resource_id, update_value)

    def _read_line(self) -> InstructionLine:
        line = self.__file.readline()
        return self.__parse_line(line)
    
    @abstractmethod
    def get_next_instruction(self) -> Instruction:
        pass

    def close(self):
        self.__file.close()

    def __del__(self):
        if hasattr(self, '__file') and self.__file is not None:
            self.__file.close()
    
