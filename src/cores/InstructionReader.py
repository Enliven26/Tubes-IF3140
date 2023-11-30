from abc import ABC, abstractmethod
from cores.Instruction import InstructionType
from cores.exceptions import InvalidInstructionLineException
from cores.Instruction import Instruction

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
        self.__is_closed = False

    def __parse_line(self, line: str) -> InstructionLine:
        # PARSE 1 LINE OF INPUT FILE

        line = line.strip()

        # Extracting information based on the format
        parts = line.split()

        if not parts:
            # Empty line
            raise InvalidInstructionLineException("Empty line found")

        if len(parts) == 1:
            raise InvalidInstructionLineException("Missing transaction id")

        instruction_type_str = parts[0].upper()
        instruction_type = InstructionType[instruction_type_str] if instruction_type_str in InstructionType.__members__ else None

        if not instruction_type:
            # Invalid instruction type
            raise InvalidInstructionLineException("Invalid instruction type found")

        transaction_id = parts[1]
        resource_id = None
        update_value = None

        if instruction_type == InstructionType.R:
            if len(parts) == 2:
                raise InvalidInstructionLineException("Missing resource id")
            
            if len(parts) > 3:
                raise InvalidInstructionLineException("Too many arguments for read instruction")

            if '=' in parts[2]:
                raise InvalidInstructionLineException("Forbidden character in resource id for read instruction: '='")
            
            # Read instruction
            resource_id = parts[2]

        elif instruction_type == InstructionType.W:

            if len(parts) > 3:
                raise InvalidInstructionLineException("Too many arguments for write instruction")
            
            if '=' not in parts[2]:
                raise InvalidInstructionLineException("Missing update value on write instruction")
            
            resource_part = parts[2].split('=')

            if len(resource_part) > 2:
                raise InvalidInstructionLineException("Too many '=' character in write instruction")

            # Write instruction
            resource_id, update_value = resource_part
            update_value = int(update_value)

        return InstructionLine(instruction_type, transaction_id, resource_id, update_value)

    def _read_line(self) -> InstructionLine:
        # READ 1 LINE OF INPUT FILE

        line = ""

        while True: 
            line = self.__file.readline()

            if not line:
                # End-of-file reached
                raise EOFError("End of file reached")
            
            line = line.strip()

            if (not line.startswith("#") and len(line)):
                break

        return self.__parse_line(line)
    
    @abstractmethod
    def _get_instruction_from_line(self, instruction_line: InstructionLine) -> Instruction:
        # GET INSTRUCTION OBJECT
        pass

    def get_next_instruction(self) -> Instruction:
        instruction_line = self._read_line()
        return self._get_instruction_from_line(instruction_line)

    def close(self):
        # CLOSE FILE READ
        self.__file.close()
        self.__is_closed = True

    def is_closed(self):
        # CHECK IF FILE IS ALREADY CLOSED
        return self.__is_closed

    def __del__(self):
        if hasattr(self, '__file') and self.__file is not None:
            self.__file.close()
    
