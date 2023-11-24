class LockUpgradeException(Exception):
    def __init__(self, message="Lock upgrade can only be done to share-lock"):
        super().__init__(message)

class LockAlreadyExistException(Exception):
        def __init__(self, message="Lock already exist"):
            super().__init__(message)

class LockNotFoundException(Exception):
     def __init__(self, message="Lock not found"):
            super().__init__(message)

class LockSharingException(Exception):
     def __init__(self, message="Lock can not be shared"):
            super().__init__(message)