from twophase.TwoPhaseInstructionReader import TwoPhaseInstructionReader
from twophase.LockManager import LockManager
from cores.ResourceManager import ResourceManager

def test():
    reader = TwoPhaseInstructionReader('input/0.txt', LockManager(), ResourceManager())
    while True:
        reader.get_next_instruction()

if __name__ == "__main__":
    test()
