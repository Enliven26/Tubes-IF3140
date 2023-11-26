from cores.Resource import Resource
from cores.LogWritter import LogWriter

class ResourceManager:
    def __init__(self) -> None:
        self.__resources: dict[str, Resource] = {}
        self.__log_writer = LogWriter("RESOURCE MANAGER")

    def _console_log(self, *args):
        self.__log_writer.console_log(*args)

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

    def print_snapshot(self):
        self.__log_writer.console_log("Resource snapshot:")
        for key, value in self.__resources.items():
            self.__log_writer.console_log("Resource", key, "=", value.get_value())

        if (not bool(self.__resources)):
            self.__log_writer.console_log("No resource data")