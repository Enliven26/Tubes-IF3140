class LogWriter:
    def __init__(self, name: str) -> None:
        self.__name = name

    def console_log(self, *args):
        formatted_message = f"[{self.__name}] " + ' '.join(map(str, args))
        print(formatted_message)

    def console_log_separator(self):
        print("===============================================================")