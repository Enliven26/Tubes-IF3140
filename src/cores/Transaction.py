class Transaction:
    def __init__(self, id: str) -> None:
        self.__id = id
        self.__is_commited = False

    def get_id(self):
        return self.__id
    
    def is_committed(self):
        return self.is_committed
    
    def commit(self):
        self.__is_commited = True