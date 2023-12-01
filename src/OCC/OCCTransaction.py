from cores.transactions import DynamicTimestampTransaction
from cores.Timestamp import TimeStamp
    
class OCCTransaction(DynamicTimestampTransaction):
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
    
    def roll_back(self):
        super().roll_back()
        self.__validation_timestamp = None
        self.__finish_timestamp = None
    
    def commit(self):
        super().commit()
        self.__finish_timestamp = TimeStamp.time()

class OCCTransactionContainer:
    def __init__(self, transaction: OCCTransaction) -> None:
        self.__transaction = transaction

    def get_id(self) -> str:
        return self.__transaction.get_id()
    
    def get_start_timestamp(self) -> float:
        return self.__transaction.get_start_timestamp()
    
    def get_validation_timestamp(self) -> float | None:
        return self.__transaction.get_validation_timestamp()
    
    def get_finish_timestamp(self) -> float | None:
        return self.__transaction.get_finish_timestamp()

    def set_validate_timestamp(self):
        self.__transaction.set_validate_timestamp()