class Transaction:
    def __init__(self, id: str) -> None:
        self.__id = id

    def get_id(self):
        return self.__id