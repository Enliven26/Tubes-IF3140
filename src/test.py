from twophase.TwoPhaseTransactionManager import TwoPhaseTransactionManager
from cores.TransactionManager import TransactionManager
import os 
from MVCC.MVCCTransactionManager import MVCCTransactionManager
from OCC.OCCTransactionManager import OCCTransactionManager

def test():

    file_name = "occ/1"
    choice = 2

    transaction_manager: TransactionManager | None = None
    file_path = os.path.join("input", file_name + ".txt")

    if (choice == 1):
        transaction_manager = TwoPhaseTransactionManager(file_path)

    elif (choice == 2):
        transaction_manager = OCCTransactionManager(file_path)

    elif (choice == 3):
        transaction_manager = MVCCTransactionManager(file_path)

    if (transaction_manager is not None):
        transaction_manager.run()
    
            

if __name__ == "__main__":
    test()
