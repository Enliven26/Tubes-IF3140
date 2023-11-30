from cores.ResourceManager import ResourceManager
from cores.LogWritter import LogWriter
from MVCC.VersionController import VersionController

class MVCCResourceHandler:
    def __init__(self) -> None:
        self.__version_controller: VersionController = VersionController()
        self.__log_writer = LogWriter("RESOURCE MANAGER")

    def read(self, resource_id: str, transaction_timestamp: float) -> int:
        # READ THE VALUE OF CERTAIN RESOURCE
        # RETURN 0 IF RESOURCE IS NEW
        return self.__version_controller.read(resource_id, transaction_timestamp)
    
    def write(self, transaction_id: str, resource_id: str, value: int) -> int:
        # UPDATE THE VALUE OF CERTAIN RESOURCE AND RETURN THE OLD VALUE
        old_value = self.__resource_manager.write(resource_id, value)
        
        transaction_history = self.__update_history.get(transaction_id)

        if (transaction_history is None):
            transaction_history = {}
            self.__update_history[transaction_id] = transaction_history

        history_list = transaction_history.get(resource_id)

        if (history_list is None):
            history_list = []
            transaction_history[resource_id] = history_list

        history_list.append((old_value, value))

        return old_value
    
    def rollback(self, transaction_id: str):
        self.__log_writer.console_log_separator()
        self.__log_writer.console_log("[ Rolling back resource values from updates of transaction", transaction_id, "]")
        transaction_history = self.__update_history.pop(transaction_id, None)
        if (transaction_history):
            for resource_id, history_list in transaction_history.items():
                oldest_value = history_list[0][0]
                current_value = self.__resource_manager.read(resource_id)

                self.__log_writer.console_log("Wrote back resource", resource_id, "from", current_value, "to", oldest_value)
                self.__resource_manager.write(resource_id, oldest_value)

        else:
            self.__log_writer.console_log("Transaction", transaction_id, "has not updated any resource")

        self.__log_writer.console_log_separator()
    
    def clear_update_history(self, transaction_id: str):
        self.__update_history.pop(transaction_id, [])

    def print_snapshot(self):
        # PRINT ALL RESOURCE VALUE AT THIS MOMENT
        self.__resource_manager.print_snapshot()
        
    


