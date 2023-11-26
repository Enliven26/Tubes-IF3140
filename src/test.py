from twophase.TwoPhaseTransactionManager import TwoPhaseTransactionManager
from cores.TransactionManager import TransactionManager
import os 

def test():

    file_name = "0"
    choice = 1

    transaction_manager: TransactionManager | None = None
    file_path = os.path.join("input", file_name + ".txt")

    if (choice == 1):
        transaction_manager = TwoPhaseTransactionManager(file_path)

    if (transaction_manager is not None):
        transaction_manager.run()
    
            

if __name__ == "__main__":
    test()
