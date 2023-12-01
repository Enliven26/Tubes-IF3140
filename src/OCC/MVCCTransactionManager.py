from cores.TransactionManager import TransactionManager
from OCC.OCCInstructionReader import OCCInstructionReader
from cores.Instruction import Instruction, InstructionType
from OCC.OCCResourceHandler import OCCResourceHandler
from collections import deque
from OCC.OCCTransaction import OCCTransaction, OCCTransactionContainer
from OCC.exceptions import FailedOCCValidation

class TransactionInfo:
    def __init__(self, transaction: OCCTransaction) -> None:
        self.transaction = transaction
        self.transaction_container = OCCTransactionContainer(transaction)

class MVCCTransactionManager(TransactionManager):

    def __init__(self, file_path: str) -> None:

        self.__resource_handler = OCCResourceHandler()
        instruction_reader = OCCInstructionReader(file_path, self.__resource_handler)

        super().__init__(instruction_reader)

        self.__transactions: dict[str, TransactionInfo] = {}
        self.__rollback_queue: deque[list[Instruction]] = deque()
        self.__done_instruction: dict[str, list[Instruction]] = {}
    
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
        self.__transactions[transaction_id].transaction.commit()
        self.__done_instruction.pop(transaction_id)

    def __execute_instruction(self, instruction: Instruction):
        transaction_id = instruction.get_transaction_id()
        instruction.execute(transaction_container=self.__transactions[transaction_id].transaction_container)
        self.__add_to_done_list(instruction)

        if (self.__is_commit_instruction(instruction)):
            self.__handle_after_commit(instruction)

    def __abort(self, transaction_id: str):
        # ADD TRANSACTION TO ROLLBACK-QUEUE
        done_instructions = self.__done_instruction.pop(transaction_id, [])
        self._console_log("Transaction", transaction_id, "is aborting")
        self.__rollback_queue.append(done_instructions)
        self.__transactions[transaction_id].transaction.roll_back()

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
            handle_rollback: bool = False
        ):
        # EXECUTE INSTRUCTION AND HANDLE ROLLBACK IF FAIL

        try:
            self.__execute_instruction(instruction)

        except FailedOCCValidation as e:

            if (not handle_rollback):
                raise e
            
            transaction_id = instruction.get_transaction_id()
            self._console_log(
                f"[ OCC Validation failed, starting rollback ]"
            )
            self.__add_to_done_list(instruction)
            self.__abort(transaction_id)
            self.__process_rollback()


    def _process_instruction(self, instruction: Instruction):
        transaction_id = instruction.get_transaction_id()
        if (self.__transactions.get(transaction_id) == None):
            transaction = OCCTransaction(transaction_id)
            self.__transactions[transaction_id] = TransactionInfo(transaction)
            
        self.__process_single_instruction(instruction, handle_rollback=True)

    def _get_next_remaining_instruction(self) -> Instruction | None:
        return None
    
    def _is_finish_or_stop(self) -> bool:
        return True
    
    def __print_transaction_status(self, transaction: OCCTransaction):

        status_str = ""

        if (transaction.is_committed()):
            status_str = "finished"

        else:
            status_str = "still going"

        validation_timestamp = transaction.get_validation_timestamp()
        finish_timestamp = transaction.get_finish_timestamp()

        self._console_log(
            "(", 
            f"Transaction ID: {transaction.get_id()},", 
            f"Start-Timestamp: {transaction.get_start_timestamp()},",
            f"Validation-Timestamp: {'-' if validation_timestamp is None else validation_timestamp},",
            f"Finish-Timestamp: {'-' if finish_timestamp is None else finish_timestamp},",
            f"Status: {status_str}",
            ")"
        )

    def _print_all_transactions_status(self):

        transactions = list(self.__transactions.values())

        self._console_log("Transaction manager stopped with status:")

        for transaction_info in transactions:
            self.__print_transaction_status(transaction_info.transaction)

        self.__resource_handler.print_snapshot()