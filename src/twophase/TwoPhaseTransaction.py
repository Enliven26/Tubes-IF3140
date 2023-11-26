from cores.Transaction import Transaction
import time

class TwoPhaseTransaction(Transaction):
    def __init__(self, id: str) -> None:
        super().__init__(id)
        self.__timestamp = time.time()

        # solve bug when timestamp for 2 transaction is equal
        time.sleep(1e-7)

    def get_timestamp(self):
        return self.__timestamp