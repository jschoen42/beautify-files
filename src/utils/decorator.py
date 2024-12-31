"""
    © Jürgen Schoenemeyer, 24.12.2024

    PUBLIC:
     - @stopwatch(text: str=None, rounds: int=1)
     - @duration(text: str="", rounds: int=1)
     - @deprecation(message: str="")

     - @retry_exception(text: str="", exception=Exception, delay: int|float=1, retries: int=5)

    PRIVAT:
      - def replace_arguments(match: Match, func_name: str, *args, **kwargs) -> str:
"""

import contextlib
import time
import re
import functools
import inspect

from typing import Any, Generator, Match
from collections.abc import Callable

from utils.trace import Trace, Color

""" Decorator '@my_decorator'

def my_decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:

        # before ...

        result = func(*args, **kwargs)

        # after ...

        return result
    return wrapper
"""

""" Decorator Factory '@my_decorator( params )'

def my_decorator( ... ) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            # before ...

            result = func(*args, **kwargs)

            # after ...

            return result
        return wrapper
    return decorator
"""

""" Decorator '@my_decorator' + Decorator Factory: '@my_decorator( params )'

# https://calmcode.io/course/decorators/optional-inputs

def my_decorator(function=None, *, ... ) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            # before ...

            result = func(*args, **kwargs)

            # after ...

            return result
        return wrapper

    if callable(function):
        return decorator(function) # Decorator
    else:
        return decorator           # Decorator Factory
"""

# @duration()
# @duration("ttx => font '{0}'")      # 0    -> args
# @duration("ttx => font '{type}'")   # type -> kwargs

# @duration("argon2 (20 rounds)", 20) # test with 20 rounds => average duration for a round

# @duration()
# @duration("{__name__} 3: {0} {1} {2}")
# @duration(text="{__name__} 4: {0} {1} {2}")

def duration(text: str=None, rounds: int=1) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            # get all input args & kwargs of the decorated function
            args_values, kwargs_values = get_args_values( func, *args, **kwargs )

            # before
            start_time = time.perf_counter()

            # decorated function
            result = func(*args, **kwargs)

            # after
            total_time = (time.perf_counter() - start_time) / rounds

            if text == "":
                pretext = ""
            elif text is None:
                pretext = func.__name__
            else:

                # replace arg, kwarg: {0} or {0|name} or {0|name} or {__name__}
                # args_values: ['Max', 99, False], kwargs_values: {'name': 'Max', 'number': 99, 'type': False}

                def replace(match: Match) -> str:
                    return replace_argument_values( match, func.__name__, args_values, kwargs_values )

                pattern = r"\{(.*?)\}"
                pretext = re.sub(pattern, replace, text)

            duration_text = f"{Color.GREEN}{Color.BOLD}{total_time:.3f} sec{Color.RESET}"
            if pretext == "":
                Trace.custom(f"{duration_text}", path="Duration")
            else:
                Trace.custom(f"{pretext}: {duration_text}", path="Duration")

            return result
        return wrapper
    return decorator

# @stopwatch
# @stopwatch()
# @stopwatch("")
# @stopwatch("{__name__} 3: {0} {1} {2}")
# @stopwatch("{__name__} 2: {name} {number} {type}")
# @stopwatch("{__name__} 1: {0|name} {1|number} {2|type}", rounds=1)
# @stopwatch(text="{__name__} 0: {0} {1} {2}", rounds=1)

def stopwatch(special=None, *, text: str=None, rounds: int=1) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            # get all input args & kwargs of the decorated function
            args_values, kwargs_values = get_args_values( func, *args, **kwargs )

            # before
            start_time = time.perf_counter()

            # decorated function
            result = func(*args, **kwargs)

            # after
            total_time = (time.perf_counter() - start_time) / rounds

            if isinstance(special, str): # text as arg
                pretext = special
            else:                        # text as kwarg
                if text is None:
                    pretext = func.__name__
                else:
                    pretext = text

            # replace arg, kwarg: {0} or {0|name} or {0|name} or {__name__}
            # args_values: ['Max', 99, False], kwargs_values: {'name': 'Max', 'number': 99, 'type': False}

            def replace(match: Match) -> str:
                return replace_argument_values( match, func.__name__, args_values, kwargs_values )

            pattern = r"\{(.*?)\}"
            pretext = re.sub(pattern, replace, pretext)

            duration_text = f"{Color.GREEN}{Color.BOLD}{total_time:.3f} sec{Color.RESET}"
            if pretext == "":
                Trace.custom(f"{duration_text}", path="Stopwatch")
            else:
                Trace.custom(f"{pretext}: {duration_text}", path="Stopwatch")

            return result
        return wrapper

    if callable(special):
        return decorator(special) # @stopwatch
    else:
        return decorator          # @stopwatch( ... )


# @deprecation()
# @deprecation("licence does not fit")

def deprecation(message: str="") -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            # before ...

            if message == "":
                Trace.custom(f"{Color.RED}'{func.__name__}' is deprecated{Color.RESET}", path="deprecation")
            else:
                Trace.custom(f"{Color.RED}'{func.__name__}' is deprecated ({message}){Color.RESET}", path="deprecation")

            result = func(*args, **kwargs)

            # after ...

            return result
        return wrapper
    return decorator

# @retry_exception(exception=ValueError)
# @retry_exception("error limit '{0}'", exception=ValueError)
# @retry_exception("ttx => font '{0}'", exception=ValueError, delay=2.5, retries=10)

def retry_exception(text: str=None, exception=Exception, delay: int|float=1, retries: int=5) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            if text is None:
                pretext = func.__name__
            else:
                def replace(match: Match) -> str:
                    return replace_arguments( match, func.__name__, *args, **kwargs )

                pattern = r"\{(.*?)\}"
                pretext = re.sub(pattern, replace, text)

            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except exception as _err:
                    attempts += 1
                    attempts_text = f"{Color.RED}{Color.BOLD}failed ({attempts}/{retries}){Color.RESET}"
                    if pretext == "":
                        Trace.custom(f"{attempts_text}", path="retry")
                    else:
                        Trace.custom(f"{pretext}: {attempts_text}", path="retry")

                    time.sleep(delay)

            raise exception
        return wrapper
    return decorator

# https://www.youtube.com/watch?v=xI4TJyd8FGk&t=860s
#
# @type_check(int, int)
#  - not for kwargs !
#  - not using the existing annotation !

def type_check(*expected_types) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            for arg, expected_type in zip(args, expected_types):
                if not isinstance(arg, expected_type):
                    Trace.error( "TypeError - expected {expected_type}, but got {type}" )

            return result
        return wrapper
    return decorator

###### decorator with ContextManager

# https://www.youtube.com/watch?v=_QXlbwRmqgI&t=260s

# BUT: arg, *kwarg not available

@contextlib.contextmanager
def duration_cm(name: str) -> Generator[None, None, None]:
    start_time = time.perf_counter()
    try:
        yield
    finally:
        end_time = time.perf_counter()
        total_time = (end_time - start_time)

        text = f"{Color.GREEN}{Color.BOLD}{total_time:.3f} sec{Color.RESET}"
        Trace.custom(f"{name}: {text}", path="duration")


# first methode to replace *args and **kwargs with values
# -> default values are not considered

def replace_arguments(match: Match, func_name: str, *args, **kwargs) -> str:
    arguments = match.group(1)

    if arguments == "__name__":
        return( func_name )

    for argument in arguments.split("|"):
        if argument.isnumeric():
            # args: {0} -> args[0]
            pos = int(argument)
            if pos < len(args):
                return str(args[pos])

        else:
            # kwargs: {type} -> kwargs["type"]
            if argument in kwargs:
                return str(kwargs.get(argument)) #

    # Trace.error(f"arg/kwarg '{arguments}' does not exist")
    # return f"'{{{arguments}}} not exist'"
    return ""

# better methode to get all args and kwargs values
# -> default values are considered

def get_args_values( func, *args, **kwargs ):
    sig = inspect.signature(func)
    bound_args = sig.bind_partial(*args, **kwargs)
    bound_args.apply_defaults()

    args_values = []
    kwargs_values = {}
    for name, value in bound_args.arguments.items():
        args_values.append(value)
        kwargs_values[name] = value

    return args_values, kwargs_values

# @stopwatch("{__name__} 1: {0|name} {1|number} {2|type}"
# args_values: ['Max', 99, False], kwargs_values: {'name': 'Max', 'number': 99, 'type': False}

def replace_argument_values(match: Match, func_name: str, args_values: list, kwargs_values: dict) -> str:
    arguments = match.group(1)

    if arguments == "__name__":
        return( func_name )

    for argument in arguments.split("|"):
        if argument.isnumeric():
            # args_values: {0} -> args_values[0]
            pos = int(argument)
            if pos < len(args_values):
                return str(args_values[pos])

        else:
            # kwargs_values: {type} -> kwargs_values["type"]
            if argument in kwargs_values:
                return str(kwargs_values.get(argument))

    return ""