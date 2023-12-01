from cores.LogWriter import LogWriter
from MVCC.exceptions import ForbiddenTimestampWriteException

class ResourceVersion:
    def __init__(
            self, 
            resource_id: str, 
            transaction_id: str = "",
            read_timestamp: float = 0, 
            write_timestamp: float = 0, 
            initial_value: int = 0
        ) -> None:

        self.__resource_id = resource_id
        self.__transaction_id = transaction_id
        self.__read_timestamp = read_timestamp
        self.__write_timestamp = write_timestamp
        self.__value = initial_value
        self.__is_committed = False

    def get_resource_id(self) -> str:
        return self.__resource_id
    
    def get_transaction_id(self) -> str:
        return self.__transaction_id
    
    def get_read_timestamp(self) -> float:
        return self.__read_timestamp
    
    def get_write_timestamp(self) -> float:
        return self.__write_timestamp
    
    def __update_read_timestamp(self, new_timestamp: float):
        self.__read_timestamp = max(self.__read_timestamp, new_timestamp)

    def get_value(self) -> int:
        return self.__value
    
    def read(self, transaction_timestamp: float) -> int:
        self.__update_read_timestamp(transaction_timestamp)
        return self.__value
    
    def update(self, value: int) -> int:
        old_value = self.__value
        self.__value = value

        return old_value
    
    def commit(self):
        self.__is_committed = True

    def is_committed(self) -> bool:
        return self.__is_committed

class VersionController:
    def __init__(self) -> None:
        # two data structure keeping the same data for read efficiency

        # 1. Map resource id to list of resource versions related to that resource id 
        self.__resource_versions: dict[str, list[ResourceVersion]] = {}
        # 2. Map transaction id to list of resource versions created to that transaction
        self.__transaction_versions: dict[str, list[ResourceVersion]] = {}

        # two data structure keeping the same data for read efficiency

        # 1. Map transaction id to list of another transaction ids that read version created by the first
        self.__version_readers: dict[str, set[str]] = {}
        # 2. Map transaction id to list of another transaction ids that create the version read by the first
        self.__version_readings: dict[str, set[str]] = {}

        self.__log_writer = LogWriter("VERSION CONTROLLER")

    def __add_reader(self, creator_transaction_id: str, reader_transaction_id: str):
        readers = self.__version_readers.get(creator_transaction_id)

        if (readers is None):
            readers = set()
            self.__version_readers[creator_transaction_id] = readers

        readers.add(reader_transaction_id)

        # write redundancy for read efficiency
        readings = self.__version_readings.get(reader_transaction_id)

        if (readings is None):
            readings = set()
            self.__version_readings[reader_transaction_id] = readings

        readings.add(creator_transaction_id)

    def __get_readers(self, creator_transaction_id: str) -> set[str]:
        return self.__version_readers.get(creator_transaction_id, set())

    def __get_or_create_resource_versions_if_not_exist(self, resource_id: str) -> list[ResourceVersion]:
        versions = self.__resource_versions.get(resource_id)

        if (versions is None):
            versions = [ResourceVersion(resource_id)]
            self.__resource_versions[resource_id] = versions

        return versions
    
    def __get_or_create_transaction_versions_if_not_exist(self, transaction_id: str) -> list[ResourceVersion]:
        versions = self.__transaction_versions.get(transaction_id)

        if (versions is None):
            versions = []
            self.__transaction_versions[transaction_id] = versions

        return versions
    
    def __get_less_or_equal_largest_version(self, resource_id: str, transaction_timestamp: float):
        # Return version of resource_id whose write timestamp is the largest write timestamp less than or equal to specified timestamp

        versions: list[ResourceVersion] = self.__get_or_create_resource_versions_if_not_exist(resource_id)

        for version in versions:
            if (version.get_write_timestamp() <= transaction_timestamp):
                return version
            
        raise Exception("Initial version not found")
    
    def read(self, resource_id: str, transaction_id: str, transaction_timestamp: float) -> int:
        # Return value of suitable version and update its read-timestamp
        version = self.__get_less_or_equal_largest_version(resource_id, transaction_timestamp)

        creator_transaction_id = version.get_transaction_id()

        # Record reading version history for cascading rollback purpose
        # Only added for version that is not committed yet and not created by the same transaction
        if (creator_transaction_id != transaction_id and not version.is_committed() and creator_transaction_id):
            self.__add_reader(creator_transaction_id, transaction_id)

        value = version.read(transaction_timestamp)

        self.__log_writer.console_log(
            "Version of resource", 
            resource_id, 
            "with write-timestamp", 
            version.get_write_timestamp(), 
            "is read with value",
            version.get_value()
        )

        return value
    
    def __insert_new_version(self, resource_id: str, transaction_id: str, transaction_timestamp: float, update_value: int):
        # Create new version of resource
        
        version = ResourceVersion(resource_id, transaction_id, transaction_timestamp, transaction_timestamp, update_value)
        versions = self.__get_or_create_resource_versions_if_not_exist(resource_id)

        insert_point = 0

        for i in range(len(versions)):
            if (versions[i].get_write_timestamp() > transaction_timestamp):
                break

            insert_point = i

        versions.insert(insert_point, version)
        
        # write redundancy for read effiency
        transaction_versions = self.__get_or_create_transaction_versions_if_not_exist(transaction_id)
        transaction_versions.append(version)

    def write(self, resource_id: str, transaction_id: str, transaction_timestamp: float, update_value: int):
        # WRITE VERSION AND RETURN OLD VALUE

        version = self.__get_less_or_equal_largest_version(resource_id, transaction_timestamp)

        if (version.get_read_timestamp() > transaction_timestamp):
            raise ForbiddenTimestampWriteException()

        if (version.get_write_timestamp() == transaction_timestamp):
            old_value = version.update(update_value)
            self.__log_writer.console_log(
                "Version of resource", 
                resource_id, 
                "with write-timestamp", 
                transaction_timestamp, 
                "is updated from",
                old_value,
                "to",
                update_value
            )

        else:
            self.__insert_new_version(resource_id, transaction_id, transaction_timestamp, update_value)
            self.__log_writer.console_log(
                "New version of resource", resource_id, "is created with timestamp", transaction_timestamp)

    def __get_cascading_rollback_transaction_ids(self, rollback_transaction_id: str) -> list[str]:
        # RETURN CASCADING READER OF EVERY VERSION BY CERTAIN TRANSACTION

        memo: dict[str, bool] = {}
        cascading_ids = []
        new_ids = [rollback_transaction_id]

        while True:

            if (len(new_ids) == 0):
                break

            current_new_ids = new_ids
            new_ids = []

            for id in current_new_ids:
                cascading_ids.append(id)
                memo[id] = True
                reader_ids = self.__get_readers(id)

                for new_reader_id in reader_ids:
                    if (not memo.get(new_reader_id)):
                        new_ids.append(new_reader_id)

        return cascading_ids

    def __rollback(self, transaction_id: str) -> list[str]:
        # REMOVE ALL VERSIONS AND DATA BY THE TRANSACTION 
        
        # removing versions created by this transaction
        transaction_versions = self.__transaction_versions.pop(transaction_id, [])

        for version in transaction_versions:
            self.__resource_versions[version.get_resource_id()].remove(version)

        # removing reding data of this transaction 
        readings = self.__version_readings.pop(transaction_id, set()) 

        # also removing this transaction from being reader of other versions
        # version reader of another transaction might be missing in cascading rollback process
        for reading in readings:
            readers = self.__version_readers.get(reading)

            if (readers is not None):
                readings.remove(transaction_id)

        # Only pop the reader list and not the reading counterpart because it will also be removed in the cascading process
        return self.__version_readers.pop(transaction_id, set())
    
    def cascade_rollback(self, transaction_id: str) -> list[str]:
        # REMOVE ALL VERSIONS AND DATA OF TRANSACTION THAT IS INVOLVED IN CASCADING ROLLBACK
        # RETURN ALL TRANSACTIONS IN THAT CASCADING ROLLBACK

        cascading_ids = self.__get_cascading_rollback_transaction_ids(transaction_id)

        for cascading_id in cascading_ids:
            self.__rollback(cascading_id)

        return cascading_ids
    
    def commit(self, transaction_id: str):
        # Remove committed transaction from reading list so it can't be rolled-back when version creator initiate cascading rollback
        readings = self.__version_readings.pop(transaction_id, set())

        for reading in readings:
            readers = self.__version_readers.get(reading)
            # the other transaction might be committed and the readers data is deleted
            if (readers):
                readers.remove(transaction_id)

        # Remove readers history that read versions created by committed transaction since committed transaction will never be rolled-back
        self.__version_readers.pop(transaction_id, set())

        # Commit version created by the transaction
        for version in self.__transaction_versions.get(transaction_id, []):
            version.commit()

    def __print_version(self, version: ResourceVersion):
        self.__log_writer.console_log(
            "(", 
            f"Write-Timestamp: {version.get_write_timestamp()},", 
            f"Read-Timestamp: {version.get_read_timestamp()},",
            f"Content-Value: {version.get_value()}",
            ")"
        )

    def print_snapshot(self):
        # PRINT ALL RESOURCE VERSIONS
        self.__log_writer.console_log("[ Resource snapshot ]")
        for resource_id, versions in self.__resource_versions.items():
            self.__log_writer.console_log(f"Versions of resource {resource_id}:")
            
            for version in versions:
                self.__print_version(version)

        if (not bool(self.__resource_versions)):
            self.__log_writer.console_log("No resource data")

        



        