from twophase.TwoPhaseTransactionManager import TwoPhaseTransactionManager
from cores.TransactionManager import TransactionManager
import os 

def get_algorithm_choice() -> int:
    print("Algorithm: ")
    print("[0] CANCEL")
    print("[1] Two Phase Locking")
    print("[2] Optimistic Concurrency Control")
    print("[3] Multiversion Timestamp Ordering Concurrency Control")

    choices = [0, 1, 2, 3]

    while True:
        try:
            choice = int(input("Choice: "))

            if (choice in choices):
                return choice
            
        except:
            print("[Input Error] Input must be integer")
        
def main():
    while True:
        file_name = input("Input file name: ")
        file_name.rstrip(".txt")
        choice = get_algorithm_choice()

        transaction_manager: TransactionManager | None = None
        file_path = os.path.join("/input", file_name, ".txt")

        if (choice == 1):
            transaction_manager = TwoPhaseTransactionManager(file_path)

        if (transaction_manager is not None):
            transaction_manager.run()
            

if __name__ == "__main__":
    main()
