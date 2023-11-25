from cores.Resource import Resource

class ResourceManager:
    def __init__(self) -> None:
        self.__resources: dict[str, Resource] = {}

    def is_resource_exist(self, id: str):
        return self.__resources.get(id) is not None
    
    def __create_resource_if_not_exist(self, id: str, value: int = 0):
        if not self.is_resource_exist(id):
            self.__resources[id] = Resource(id, value)

    def read(self, id: str) -> int:

        self.__create_resource_if_not_exist(id)
        resource = self.__resources.get(id)
        return resource.get_value()
    
    def write(self, id: str, value: int):
        self.__create_resource_if_not_exist(id)
        resource = self.__resources.get(id)
        old_value = resource.get_value()
        resource.set_value(value)
        return old_value