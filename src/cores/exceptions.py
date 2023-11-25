# class ResourceNotFoundException(Exception):
#     def __init__(self, message="Resource not found"):
#         super().__init__(message)

class InvalidInstructionLineException(Exception):
    def __init__(self, message="Invalid instruction line found in input file"):
        super().__init__(message)