from cores.TransactionManager import TransactionManager
from twophase.TwoPhaseInstructionReader import TwoPhaseInstructionReader
from cores.Instruction import Instruction, InstructionType
from twophase.LockManager import LockManager
from twophase.TwoPhaseResourceHandler import TwoPhaseResourceHandler
from collections import deque
from cores.transactions import StaticTimestampTransaction
from twophase.exceptions import LockSharingException


class TwoPhaseTransactionManager(TransactionManager):

    # CORRECT ASSUMPTION:

    # 1. It's IMPOSSIBLE that instructions from the same transaction can be in both wait-queue and rollback-queue. instructions in rollback queue will be executed right after 1 instruction that trigger the abort and if that rollback instructions can't be executed, it will be put in wait-queue

    # 2. Because of point number 1, it's impossible that instructions in wait-queue of certain transaction is out of order.

    def __init__(self, file_path: str) -> None:

        self.__lock_manager = LockManager()
        self.__resource_handler = TwoPhaseResourceHandler()
        instruction_reader = TwoPhaseInstructionReader(file_path, self.__lock_manager, self.__resource_handler)

        super().__init__(instruction_reader)

        self.__transactions: dict[str, StaticTimestampTransaction] = {}
        self.__wait_queue: deque[Instruction] = deque()
        self.__rollback_queue: deque[list[Instruction]] = deque()
        self.__done_instruction: dict[str, list[Instruction]] = {}
        self.__has_transaction_committed: bool = False

    def __is_oldest(self, transaction_id: str, conflict_transaction_ids: list[str]):
        # CHECK IF TRANSACTION IS THE OLDEST AMONG LOCK HOLDERS OF CERTAIN RESOURCE
        transaction = self.__transactions[transaction_id]
        for conflict_transaction_id in conflict_transaction_ids:
            conflict_transaction = self.__transactions[conflict_transaction_id]
            if (transaction.get_timestamp() > conflict_transaction.get_timestamp()):
                return False
            
        return True
    
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
        self.__transactions[transaction_id].commit()
        self.__done_instruction.pop(transaction_id)
        self.__resource_handler.clear_update_history(transaction_id)

    def __execute_instruction(self, instruction: Instruction):
        instruction.execute()
        self.__add_to_done_list(instruction)

        if (self.__is_commit_instruction(instruction)):
            self.__handle_after_commit(instruction)

    def __pop_instructions_from_queue(self, transaction_id: str):
        # REMOVE ALL INSTRUCTIONS OF TRANSACTION_ID FROM WAIT QUEUE AND RETURN IT
        instructions = []
        for instruction in self.__wait_queue:
            if (instruction.get_transaction_id() == transaction_id):
                instructions.append(instruction)
        
        for instruction in instructions:
            self.__wait_queue.remove(instruction)

        return instructions

    def __abort(self, transaction_id: str):
        # ADD TRANSACTION TO ROLLBACK-QUEUE
        done_instructions = self.__done_instruction.pop(transaction_id, [])
        waiting_instructions = self.__pop_instructions_from_queue(transaction_id)
        done_instructions.extend(waiting_instructions)
        self._console_log("Transaction", transaction_id, "is aborting")
        self.__resource_handler.rollback(transaction_id)
        self.__lock_manager.unlock_all(transaction_id)
        self.__rollback_queue.append(done_instructions)
        self.__transactions[transaction_id].roll_back()

    def __abort_all(self, transaction_ids: list[str]):
        # ADD LIST OF TRANSACTION TO ROLLBACK-QUEUE
        for transaction_id in transaction_ids:
            self.__abort(transaction_id)

    def __dequeue_from_rollback(self):
        # ROLLBACK TRANSACTION THAT IS IN FRONT OF THE ROLLBACK-QUEUE
        instructions = self.__rollback_queue.popleft()
        transaction_id = instructions[0].get_transaction_id()
        self.__transactions[transaction_id].reset_status()
        self._console_log("Trying to rollback transaction", instructions[0].get_transaction_id())
        return instructions

    def __wait(self, instruction: Instruction):
        # ADD INSTRUCTION TO WAIT-QUEUE
        self.__wait_queue.append(instruction)
        self.__transactions[instruction.get_transaction_id()].wait()
        self._console_log("Instruction", instruction, "entered wait-queue")

    def __unwait(self) -> Instruction:
        # TRY TO EXECUTE INSTRUCTION THAT IS IN FRONT OF THE WAIT-QUEUE
        instruction = self.__wait_queue.popleft()
        self._console_log("Instruction", instruction, "leave wait-queue")
        return instruction
    
    def __is_in_queue(self, transaction_id):
        # CHECK IF TRANSACTION IS WAITING OR ROLLING BACK
        transaction = self.__transactions.get(transaction_id)

        if (transaction is None):
            return False
        
        return transaction.is_waiting() or transaction.is_rolling_back()

    def __process_single_instruction(
            self, 
            instruction: Instruction, 
            process_post_rollback: bool = False, 
            process_post_commit: bool = False
        ):
        # EXECUTE INSTRUCTION AND HANDLE WAITING AND ROLLING BACK INSTRUCTION AFTER EXECUTION
        instruction_id = instruction.get_transaction_id()
        if (self.__is_in_queue(instruction_id)):
            self._console_log("[ Transaction", instruction_id,  "is waiting for previous instructions ]")
            self.__wait(instruction)
            return

        while True:
            try:
                self.__execute_instruction(instruction)
                
                if (process_post_rollback and len(self.__rollback_queue) > 0):
                    self.__process_rollback()

                if (process_post_commit and self.__has_transaction_committed):
                    self.__process_wait()

                break


            except LockSharingException as e:
                transaction_ids = e.get_conflict_transaction_ids()

                if (self.__is_oldest(instruction.get_transaction_id(), transaction_ids)):
                    self.__abort_all(transaction_ids)
                
                else:
                    self.__wait(instruction)
                    break

    def __process_wait(self):
        # EXECUTE ALL INSTRUCTION IN WAIT-QUEUE AND HANDLE ROLLBACK-QUEUE
        while self.__has_transaction_committed:
            self.__has_transaction_committed = False
            first_waiting_instruction_occurrence: dict[str, bool] = {}

            count = len(self.__wait_queue)

            for _ in range(count):
                instruction = self.__unwait()
                transaction_id = instruction.get_transaction_id()

                if (not first_waiting_instruction_occurrence.get(transaction_id)):
                    first_waiting_instruction_occurrence[transaction_id] = True
                    self.__transactions[transaction_id].reset_status()

                self.__process_single_instruction(instruction, process_post_rollback=True)

    def __process_rollback(self):
        # EXECUTE ALL ROLLBACK INSTRUCTIONS
        while(len(self.__rollback_queue) > 0):
            instructions = self.__dequeue_from_rollback()

            for instruction in instructions:
                self.__process_single_instruction(instruction)
    
    def _get_next_remaining_instruction(self) -> Instruction | None:
        return None

    def _process_instruction(self, instruction: Instruction):
        transaction_id = instruction.get_transaction_id()
        if (self.__transactions.get(transaction_id) == None):
            self.__transactions[transaction_id] = StaticTimestampTransaction(transaction_id)
            
        self.__process_single_instruction(
            instruction, 
            process_post_rollback=True,
            process_post_commit=True
        )

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

        for instruction in self.__wait_queue:
            self._console_log("Instruction", instruction, "is in wait-queue")

        self.__resource_handler.print_snapshot()

    def _is_finish_or_stop(self) -> bool:
        return True