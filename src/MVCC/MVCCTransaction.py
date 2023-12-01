from cores.transactions import DynamicTimestampTransaction

class MVCCTransaction(DynamicTimestampTransaction):
    def __init__(self, id: str) -> None:
        super().__init__(id)

    def get_timestamp(self) -> float:
        return self._get_timestamp()
    
class MVCCTransactionContainer:
    def __init__(self, transaction: MVCCTransaction) -> None:
        self.__transaction = transaction

    def get_id(self) -> str:
        return self.__transaction.get_id()
    
    def get_timestamp(self) -> float:
        return self.__transaction.get_timestamp()
