from cores.Transaction import Transaction
import timeit
import time

class TwoPhaseTransaction(Transaction):
    def __init__(self, id: str) -> None:
        super().__init__(id)
        self.__timestamp = timeit.timeit()

        # solve bug when timestamp for 2 transaction is equal
        time.sleep(0.01)

    def get_timestamp(self):
        return self.__timestamp