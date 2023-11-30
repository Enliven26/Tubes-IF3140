from cores.TransactionManager import TransactionManager
from MVCC.MVCCInstructionReader import MVCCInstructionReader
from cores.Instruction import Instruction, InstructionType
from MVCC.VersionController import VersionController
from collections import deque
from cores.transactions import DynamicTimestampTransaction
from MVCC.instructions import MVCCTransactionContainer
from MVCC.exceptions import ForbiddenTimestampWriteException

class TransactionInfo:
    def __init__(self, transaction: DynamicTimestampTransaction) -> None:
        self.transaction = transaction
        self.transaction_container = MVCCTransactionContainer(transaction)

class TwoPhaseTransactionManager(TransactionManager):

    # CORRECT ASSUMPTION:

    # 1. MVTO doesn't ensure recoverability and cascadelessness
    # 2. Starvation because of rollback is impossible since every instructions from rolled-back transaction will be prioritized and might commit (if last instruction of the rolled-back transaction is accepted) before new instructions are processed. (Note that it only starve if instructions of the transaction never end [infinite instructions].)

    def __init__(self, file_path: str) -> None:

        self.__version_controller = VersionController()
        instruction_reader = MVCCInstructionReader(file_path, self.__version_controller)

        super().__init__(instruction_reader)

        self.__transactions: dict[str, TransactionInfo] = {}
        self.__rollback_queue: deque[list[Instruction]] = deque()
        self.__done_instruction: dict[str, list[Instruction]] = {}
        self.__has_transaction_committed: bool = False
    
    def __add_to_done_list(self, instruction: Instruction) -> bool:
        # ADD INSTRUCTION TO DONE LIST FOR ROLLBACK PURPOSE
        transaction_id = instruction.get_transaction_id()
        done_instructions = self.__done_instruction.get(transaction_id)

        if (done_instructions is None):
            done_instructions = []
            self.__done_instruction[transaction_id] = done_instructions

        done_instructions.append(instruction)

    def __is_commit_instruction(self, instruction: Instruction) -> bool:
        return instruction.get_transaction_type() == InstructionType.C
    
    def __handle_after_commit(self, instruction: Instruction) -> bool:
        # CLEAR DATA OF TRANSACTION AFTER COMMIT IF NECESSARY
        transaction_id = instruction.get_transaction_id()
        self.__has_transaction_committed = True
        self.__transactions[transaction_id].transaction.commit()
        self.__done_instruction.pop(transaction_id)

    def __execute_instruction(self, instruction: Instruction):
        instruction.execute()
        self.__add_to_done_list(instruction)

        if (self.__is_commit_instruction(instruction)):
            self.__handle_after_commit(instruction)

    def __abort(self, transaction_id: str):
        # ADD TRANSACTION TO ROLLBACK-QUEUE
        done_instructions = self.__done_instruction.pop(transaction_id, [])
        self._console_log("Transaction", transaction_id, "is aborting")
        self.__version_controller.rollback(transaction_id)
        self.__rollback_queue.append(done_instructions)
        self.__transactions[transaction_id].transaction.roll_back()

    def __abort_all(self, transaction_ids: list[str]):
        # ADD LIST OF TRANSACTION TO ROLLBACK-QUEUE
        for transaction_id in transaction_ids:
            self.__abort(transaction_id)

    def __dequeue_from_rollback(self):
        # ROLLBACK TRANSACTION THAT IS IN FRONT OF THE ROLLBACK-QUEUE
        instructions = self.__rollback_queue.popleft()
        transaction_id = instructions[0].get_transaction_id()
        self.__transactions[transaction_id].transaction.reset_status()
        self._console_log("Trying to rollback transaction", instructions[0].get_transaction_id())
        return instructions
    
    def __process_rollback(self):
        # EXECUTE ALL ROLLBACK INSTRUCTIONS
        while(len(self.__rollback_queue) > 0):
            instructions = self.__dequeue_from_rollback()

            for instruction in instructions:
                self.__process_single_instruction(instruction)

    def __process_single_instruction(
            self, 
            instruction: Instruction, 
            process_post_rollback: bool = False, 
            process_post_commit: bool = False
        ):
        # EXECUTE INSTRUCTION AND HANDLE WAITING AND ROLLING BACK INSTRUCTION AFTER EXECUTION
        instruction_id = instruction.get_transaction_id()

        try:
            self.__execute_instruction(instruction)

        except ForbiddenTimestampWriteException as e:
            transaction_ids = e.get_cascading_rollback_transaction_ids()
            self.__abort_all(transaction_ids)
            self.__process_rollback()


    def _process_instruction(self, instruction: Instruction):
        transaction_id = instruction.get_transaction_id()
        if (self.__transactions.get(transaction_id) == None):
            self.__transactions[transaction_id] = DynamicTimestampTransaction(transaction_id)
            
        self.__process_single_instruction(
            instruction, 
            process_post_rollback=True,
            process_post_commit=True
        )

    def _get_next_remaining_instruction(self) -> Instruction | None:
        return None
    
    def _is_finish_or_stop(self) -> bool:
        return True

    def _print_all_transactions_status(self):

        transactions = list(self.__transactions.values())

        self._console_log("Transaction manager stopped with status:")

        for transaction_info in transactions:
        
            status_str = ""

            if (transaction_info.transaction.is_committed()):
                status_str = "finished"

            else:
                status_str = "still going"

            self._console_log("Transaction", transaction_info.transaction.get_id(), "is", status_str)

        self.__version_controller.print_snapshot()