from enum import Enum

class TransactionStatus(Enum):
    GOING = 0
    WAITING = 1
    ROLLINGBACK = 2
    COMMITTED = 3

class Transaction:
    def __init__(self, id: str) -> None:
        self.__id = id
        self.__status = TransactionStatus.GOING

    def get_id(self):
        return self.__id
    
    def reset_status(self):
        self.__status = TransactionStatus.GOING
    
    def is_rolling_back(self):
        return self.__status == TransactionStatus.ROLLINGBACK
    
    def roll_back(self):
        self.__status = TransactionStatus.ROLLINGBACK
    
    def is_waiting(self):
        return self.__status == TransactionStatus.WAITING
    
    def wait(self):
        self.__status = TransactionStatus.WAITING
    
    def is_committed(self):
        return self.__status == TransactionStatus.COMMITTED
    
    def commit(self):
        self.__status = TransactionStatus.COMMITTED