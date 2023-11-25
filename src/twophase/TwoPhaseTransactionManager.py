from cores.TransactionManager import TransactionManager
from twophase.TwoPhaseInstructionReader import TwoPhaseInstructionReader
from cores.Instruction import Instruction, InstructionType
from twophase.LockManager import LockManager
from cores.ResourceManager import ResourceManager
from queue import Queue
from twophase.TwoPhaseTransaction import TwoPhaseTransaction
from twophase.exceptions import LockSharingException


class TwoPhaseTransactionManager(TransactionManager):
    def __init__(self, file_path: str) -> None:

        self.__lock_manager = LockManager()
        resource_manager = ResourceManager()
        instruction_reader = TwoPhaseInstructionReader(file_path, self.__lock_manager, resource_manager)

        super().__init__(resource_manager, instruction_reader)

        self.__transactions: dict[str, TwoPhaseTransaction] = {}
        self.__wait_queue: Queue[Instruction] = Queue(-1)
        self.__rollback_queue: Queue[list[Instruction]] = Queue(-1)
        self.__done_instruction: dict[str, list[Instruction]] = {}
        self.__has_transaction_committed: bool = False

    def __is_oldest(self, transaction_id: str, conflict_transaction_ids: list[str]):
        transaction = self.__transactions[transaction_id]

        for conflict_transaction_id in conflict_transaction_ids:
            conflict_transaction = self.__transactions[conflict_transaction_id]
            if (transaction.get_timestamp() > conflict_transaction.get_timestamp()):
                return False
            
        return True
            
    def _get_next_remaining_instruction(self) -> Instruction:
        pass

    def __is_commit_instruction(self, instruction: Instruction) -> bool:
        return instruction.get_transaction_type() == InstructionType.C
    
    def __update_has_commit_status(self, instruction: Instruction) -> bool:
        if (self.__is_commit_instruction(instruction)):
            self.__has_transaction_committed = True

    def __execute_instruction(self, instruction: Instruction):
        instruction.execute()
        self.__update_has_commit_status(instruction)

    def __process_wait(self):
        pass

    def __process_rollback(self):
        pass

    def __abort(self, transaction_id: str):
        done_instructions: list[Instruction] = self.__done_instruction.pop(transaction_id, [])
        self.__rollback_queue.put(done_instructions)
        self.__lock_manager.unlockAll(transaction_id)

    def __abort_all(self, transaction_ids: list[str]):
        for transaction_id in transaction_ids:
            self.__abort(transaction_id)

    def __wait(self, instruction: Instruction):
        self.__wait_queue.put(instruction)
    
    def _process_instruction(self, instruction: Instruction):
        try:
            self.__execute_instruction(instruction)
            
            if (not self.__rollback_queue.empty()):
                self.__process_rollback()

            if (self.__has_transaction_committed):
                self.__process_wait()


        except LockSharingException as e:
            transaction_ids = e.get_conflict_transaction_ids()

            if (self.__is_oldest(instruction.get_transaction_id(), transaction_ids)):
                self.__abort_all(transaction_ids)
            
            else:
                self.__wait(instruction)

    def _print_all_transactions_status(self):

        transactions = list(self.__transactions.values())

        self._console_log("Transaction manager stopped with status:")

        for transaction in transactions:
        
            status_str = ""

            if (transaction.is_committed()):
                status_str = "finished"

            else:
                status_str = "still going"

            self._console_log("Transaction", transaction.get_id(), "is", status_str)

    def _is_finish_or_stop(self) -> bool:
        pass