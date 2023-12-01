from cores.transactions import DynamicTimestampTransaction

class MVCCTransaction(DynamicTimestampTransaction):
    def __init__(self, id: str) -> None:
        super().__init__(id)

    def get_timestamp(self) -> float:
        return self._get_timestamp()
