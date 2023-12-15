from time import monotonic
from datetime import datetime, timedelta
from logging import info, basicConfig, DEBUG


def output_msg(string: str) -> None:
    "Prints the date and time of action + info specified in str"
    # info(f"{string}")
    print(f"[{str(datetime.now())}] {string}")


def my_logs_global_config(filepath: str):
    basicConfig(format='%(asctime)s %(message)s', datefmt='[%m/%d/%Y %I:%M:%S %p]', filename=f"{filepath}.log",
                encoding='utf-8', level=DEBUG)


def my_function_timer(arg: str):
    """
    Decorator ; prints out execution time of decorated func
    * arg : descrptor name of job
    """
    def my_inner_dec(func):
        def wrapper(*args, **kwargs):
            output_msg("Starting job...")
            start_time = monotonic()
            res = func(*args, **kwargs)
            end_time = monotonic()
            output_msg(
                f"{arg} : Finished after {timedelta(seconds=end_time - start_time)} seconds")
            return res
        return wrapper
    return my_inner_dec
