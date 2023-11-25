class Resource:
    def __init__(self, id: str, value: int) -> None:
        self.__id = id
        self.__value = value

    def get_id(self):
        return self.__id
    
    def get_value(self):
        return self.__value
    
    def set_value(self, value: int):
        self.__value = value