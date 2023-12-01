from cores.Resource import Resource
from cores.LogWriter import LogWriter

class ResourceManager:
    def __init__(self) -> None:
        self.__resources: dict[str, Resource] = {}
        self.__log_writer = LogWriter("RESOURCE MANAGER")

    def _console_log(self, *args):
        # USE THIS FOR PRINTING FROM RESOURCE MANAGER PERSPECTIVE
        self.__log_writer.console_log(*args)

    def __is_resource_exist(self, id: str) -> bool:
        return self.__resources.get(id) is not None
    
    def __create_resource_if_not_exist(self, id: str, value: int = 0):
        # RESOURCE HAS VALUE 0 BY DEFAULT
        if not self.__is_resource_exist(id):
            self.__resources[id] = Resource(id, value)

    def read(self, id: str) -> int:
        # READ THE VALUE OF CERTAIN RESOURCE
        # RETURN 0 IF RESOURCE IS NEW
        self.__create_resource_if_not_exist(id)
        resource = self.__resources.get(id)
        return resource.get_value()
    
    def write(self, id: str, value: int) -> int:
        # UPDATE THE VALUE OF CERTAIN RESOURCE AND RETURN THE OLD VALUE
        self.__create_resource_if_not_exist(id)
        resource = self.__resources.get(id)
        old_value = resource.get_value()
        resource.set_value(value)
        return old_value

    def print_snapshot(self):
        # PRINT ALL RESOURCE VALUE AT THIS MOMENT
        self.__log_writer.console_log("[ Resource snapshot ]")
        for key, value in self.__resources.items():
            self.__log_writer.console_log("Resource", key, "=", value.get_value())

        if (not bool(self.__resources)):
            self.__log_writer.console_log("No resource data")

    def get_snapshot(self) -> dict[str, int]:
        snapshot: dict[str, int] = {}

        for resource_id, resource in self.__resources.items():
            snapshot[resource_id] = resource.get_value()

        return snapshot