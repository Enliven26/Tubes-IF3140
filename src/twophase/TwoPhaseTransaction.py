from cores.Transaction import Transaction
import time

class TwoPhaseTransaction(Transaction):
    def __init__(self, id: str) -> None:
        super().__init__(id)
        self.__timestamp = time.time()

    def get_timestamp(self):
        return self.__timestamp