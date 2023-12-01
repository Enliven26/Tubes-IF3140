from cores.transactions import StaticTimestampTransaction
from cores.transactions import TransactionStatus

class TwoPhaseTransaction(StaticTimestampTransaction):
    def __init__(self, id: str) -> None:
        super().__init__(id)

    def get_timestamp(self) -> float:
        return self._get_timestamp()

    def is_waiting(self) -> bool:
        return self._get_status == TransactionStatus.WAITING
    
    def wait(self):
        self._set_status(TransactionStatus.WAITING)