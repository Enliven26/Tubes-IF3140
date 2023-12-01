from cores.ResourceManager import ResourceManager
from cores.LogWriter import LogWriter
from OCC.OCCTransaction import OCCTransactionContainer
from OCC.exceptions import ForbiddenOptimisticCommit
class OCCResourceHandler:
    def __init__(self) -> None:
        self.__resource_manager: ResourceManager = ResourceManager()
        self.__log_writer = LogWriter("RESOURCE MANAGER")

        # Write history format for certain transaction id: 
        # list of resource id that is written
        self.__write_history: dict[str, list[str]] = {}

        # Read history format for certain transaction id: 
        # list of resource id that is read
        self.__read_history: dict[str, list[str]] = {}

        # Snapshot record of certain transaction id
        # Snapshot is in form of dict with key: resource id and value: value of the resource
        self.__snapshots: dict[str, dict[str, int]] = {}

        self.__transaction_containers: dict[str, OCCTransactionContainer] = []

    def __add_transaction_if_not_exist(self, transaction_container: OCCTransactionContainer):
        transaction_id = transaction_container.get_id()
        
        if (self.__transaction_containers.get(transaction_id) is None):
            self.__transaction_containers[transaction_id] = transaction_container


    def __add_read_history(self, transaction_id: str, resource_id: str):
        history = self.__read_history.get(transaction_id)

        if (history is None):
            history = []
            self.__read_history[transaction_id] = history

        history.append(resource_id)

    def __add_write_history(self, transaction_id: str, resource_id: str):
        history = self.__write_history.get(transaction_id)

        if (history is None):
            history = []
            self.__write_history[transaction_id] = history

        history.append(resource_id)

    def __get_or_create_snapshot(self, transaction_id) -> dict[str, int]:
        snapshot = self.__snapshots.get(transaction_id)

        if (snapshot is None):
            snapshot = self.__resource_manager.get_snapshot()
            self.__snapshots[transaction_id] = snapshot

        return snapshot

    def read(self, transaction_container: OCCTransactionContainer, resource_id: str) -> int:
        # READ THE VALUE OF CERTAIN RESOURCE IN SNAPSHOT
        # RETURN 0 IF RESOURCE IS NEW

        self.__add_transaction_if_not_exist(transaction_container)

        transaction_id = transaction_container.get_id()

        snapshot = self.__get_or_create_snapshot(transaction_id)

        value = snapshot.get(resource_id)

        if (value is None):
            value = 0
            snapshot[resource_id] = value

        self.__add_read_history(transaction_id, resource_id)

        return value
    
    def write(self, transaction_container: OCCTransactionContainer, resource_id: str, value: int) -> int:
        # UPDATE THE VALUE OF CERTAIN RESOURCE IN SNAPSHOT AND RETURN THE OLD VALUE

        self.__add_transaction_if_not_exist(transaction_container)

        transaction_id = transaction_container.get_id()

        snapshot = self.__get_or_create_snapshot(transaction_id)

        old_value = snapshot.get(resource_id)

        if (value is None):
            old_value = 0

        snapshot[resource_id] = value

        self.__add_write_history(transaction_id, resource_id)
        
        return old_value
    
    def __clear_data(self, transaction_id: str):
        self.__read_history.pop(transaction_id, [])
        self.__write_history.pop(transaction_id, [])
        self.__snapshots.pop(transaction_id, [])

    def rollback(self, transaction_id: str):
        self.__clear_data(transaction_id)

    def __write_commit(self, transaction_id: str):
        snapshot = self.__get_or_create_snapshot(transaction_id)
        write_history = self.__write_history.get(transaction_id, [])

        for resource_id in write_history:
            self.__resource_manager.write(resource_id, snapshot[resource_id])

    def __validate(self, transaction_id: str) -> bool:
        # VALIDATE TRANSACTION BEFORE COMMIT

        self.__log_writer.console_log(f"[ Validating transaction {transaction_id} before commit ]")

        # TODO: CEK VALIDASI BERDASARKAN ALGORITMA OCC
        # ATRIBUT YANG PERLU DIAKSES: 
        # SELF.__TRANSACTION_CONTAINERS, ISINYA SEMUA TRANSACTION YG PERNAH DICATAT
        # SELF.__write_history dan self.read_history, baca apa isinya di __init__ atas dan guna datanya di ppt

        # LIHAT ATRIBUT YANG BISA DI AKSES DARI TRANSACTIONCONTAINER DI FILE OCCTRANSACTION
        # EDGE CASE: TRANSACTION SAAT INI (SESUAI PARAMETER TRANSACTION_ID) GA KETEMU DI ATRIBUT CONTAINERS, ITU LANGSUNG RETURN TRUE AJA KARENA ARTINYA DIA GA PERNAH READ/WRITE
        return True

    def commit(self, transaction_id: str):

        if (not self.__validate(transaction_id)):
            raise ForbiddenOptimisticCommit()
        
        self.__write_commit(transaction_id)
        self.__clear_data(transaction_id)

    def print_snapshot(self):
        # PRINT ALL RESOURCE VALUE AT THIS MOMENT
        self.__resource_manager.print_snapshot()
        
    


