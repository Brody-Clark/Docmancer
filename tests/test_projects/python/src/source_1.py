# Test file for parsing and documentation generation

database = Database()


class InvalidUserException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


# This function should be skipped since it is commented out
# def func_1():
#     print("helo")


def string_manip(s: str) -> str:
    """
    _summary_

    Args:
        _name_ (_type_): _description_

    Returns:
        _returns_
    """
    s = s[::-1]
    return s


def optional_return() -> str | None:
    return "Hello"


def login(user, p):

    if len(user) == 0 or len(p) == 0:
        raise ValueError("field cannot be empty")
    try:
        database.login(user, p)
    except Exception as e:
        print(e)
        raise InvalidUserException(f"{user} not found")


class Math:

    def calculate_area(self, length, width):

        return length * width

    def calc(self, perimeter: int, num: int, other_num: float):

        if other_num < 0:
            raise ValueError("other_num must be positive")
        perimeter = num + 1 + other_num
        return perimeter


def basic_typed(a: int, b: str, c: float):
    pass


def unions(a: int | str, b: list[int | None]):
    pass


from typing import Union, Optional


def typing_unions(a: Union[int, str], b: Optional[int]):
    pass


def splats(*args, **kwargs):
    pass


def typed_splats(*args: int, **kwargs: str):
    pass


def kw_only(a: int, *, b: str, c: float = 3.14):
    pass
