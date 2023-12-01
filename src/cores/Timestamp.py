import time

class TimeStamp:
    @staticmethod
    def time():
        # solve bug when timestamp for 2 transaction is equal
        time.sleep(1e-7)
        return time.time()