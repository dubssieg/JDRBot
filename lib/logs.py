from datetime import datetime


def output_msg(string: str) -> None:
    """Prints the date and time of action + info specified in str"""
    print(f"[{str(datetime.now())}] {string}")


##################### CUSTOM ERRORS & STACK ##########################


class OBS_Shutdown(BaseException):
    """Custom error for OBS not working"""

    def __init__(self, msg: str) -> None:
        self.__message = msg
        super().__init__(self.__message)


class Max_Poll_Size(BaseException):
    """Custom error for OBS not working"""

    def __init__(self, msg: str) -> None:
        self.__message = msg
        super().__init__(self.__message)


class Wrapped_Exception(BaseException):
    """Custom error for OBS not working"""

    def __init__(self, msg: str) -> None:
        self.__message = msg
        super().__init__(self.__message)


class Sheets_Exception(BaseException):
    """Custom error for OBS not working"""

    def __init__(self, msg: str, context) -> None:
        self.__message = msg
        super().__init__(self.__message)
