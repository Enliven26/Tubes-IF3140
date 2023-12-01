from enum import Enum
from cores.Timestamp import TimeStamp

class TransactionStatus(Enum):
    GOING = 0
    WAITING = 1
    ROLLINGBACK = 2
    COMMITTED = 3

class Transaction:
    def __init__(self, id: str) -> None:
        self.__id = id
        self.__status = TransactionStatus.GOING

    def get_id(self) -> str:
        return self.__id
    
    def reset_status(self):
        self.__status = TransactionStatus.GOING
    
    def is_rolling_back(self) -> bool:
        return self.__status == TransactionStatus.ROLLINGBACK
    
    def roll_back(self):
        self.__status = TransactionStatus.ROLLINGBACK
    
    def is_waiting(self) -> bool:
        return self.__status == TransactionStatus.WAITING
    
    def wait(self):
        self.__status = TransactionStatus.WAITING
    
    def is_committed(self) -> bool:
        return self.__status == TransactionStatus.COMMITTED
    
    def commit(self):
        self.__status = TransactionStatus.COMMITTED

class StaticTimestampTransaction(Transaction):
    def __init__(self, id: str) -> None:
        super().__init__(id)
        self.__timestamp = TimeStamp.time()

    def _get_timestamp(self) -> float:
        return self.__timestamp
    
class DynamicTimestampTransaction(Transaction):
    def __init__(self, id: str) -> None:
        super().__init__(id)
        self.__timestamp = 0
        self.__reset_timestamp()

    def __reset_timestamp(self):
        self.__timestamp = TimeStamp.time()

    def _get_timestamp(self) -> float:
        return self.__timestamp
    
    def roll_back(self):
        super().roll_back()
        self.__reset_timestamp()

