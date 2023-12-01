class FailedOCCValidation(Exception):
    def __init__(self, 
                 message="OCC Validation Failed"):
        super().__init__(message)
        self.__message = message

    def get_message(self):
        return self.__message
