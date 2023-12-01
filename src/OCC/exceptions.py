class FailedOCCValidation(Exception):
    def __init__(self, 
                 message="OCC Validation Failed"):
        super().__init__(message)
