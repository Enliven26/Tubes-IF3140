from cores.transactions import DynamicTimestampTransaction
from cores.Timestamp import TimeStamp

class MVCCTransaction(DynamicTimestampTransaction):
    def __init__(self, id: str) -> None:
        super().__init__(id)
        self.__validation_timestamp: float | None = None
        self.__finish_timestamp: float | None = None

    def get_start_timestamp(self) -> float:
        return self._get_timestamp()
    
    def get_validation_timestamp(self) -> float | None:
        return self.__validation_timestamp
    
    def get_finish_timestamp(self) -> float | None:
        return self.__finish_timestamp
    
    def set_validate_timestamp(self):
        self.__validation_timestamp = TimeStamp.time()
    
    def commit(self):
        super().commit()
        self.__finish_timestamp = TimeStamp.time()

