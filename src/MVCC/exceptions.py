class ForbiddenTimestampWriteException(Exception):
    def __init__(self, 
                 message="Resource to be written has read timestamp that is larger than transaction timestamp"):
        super().__init__(message)
