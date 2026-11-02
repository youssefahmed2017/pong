"""Asking the user for input. Bad answers are explained and asked again.

    from easyutils import ask

    name = ask.text("What's your name? ")
    age = ask.number("How old are you? ", whole=True, min=0)
    if ask.yes_no("Play again?"):
        ...
    color = ask.choice("Pick a color:", ["red", "green", "blue"])
    secret = ask.password("New password: ", confirm=True, min_length=8)
"""

from __future__ import annotations

import getpass
from typing import List, Optional, Sequence, TypeVar, Union

__all__ = ["text", "number", "yes_no", "choice", "password"]

T = TypeVar("T")

_YES = {"y", "yes", "true", "1"}
_NO = {"n", "no", "false", "0"}


def text(prompt: str = "", allow_empty: bool = False) -> str:
    """Ask for some text. Empty answers are refused unless allow_empty=True."""
    while True:
        answer = input(prompt).strip()
        if answer or allow_empty:
            return answer
        print("Please type something.")


def number(
    prompt: str = "",
    whole: bool = False,
    min: Optional[float] = None,
    max: Optional[float] = None,
) -> Union[int, float]:
    """Ask for a number. Keeps asking until the answer is a valid number.

    Answers like "7" come back as int and "7.5" as float.
    With whole=True only whole numbers are accepted.
    Use min and max to set the allowed range (both inclusive).
    """
    while True:
        answer = input(prompt).strip()
        try:
            value: Union[int, float] = int(answer)
        except ValueError:
            try:
                value = float(answer)
            except ValueError:
                print(f"'{answer}' is not a number. Please try again.")
                continue
            if whole:
                print("Please type a whole number (no decimals).")
                continue
        if min is not None and value < min:
            print(f"Please type a number of at least {min}.")
            continue
        if max is not None and value > max:
            print(f"Please type a number of at most {max}.")
            continue
        return value


def yes_no(prompt: str = "", default: Optional[bool] = None) -> bool:
    """Ask a yes/no question. Accepts y, yes, n, no (any capitalization).

    With a default, pressing Enter on its own picks the default.
    """
    if default is True:
        hint = " [Y/n] "
    elif default is False:
        hint = " [y/N] "
    else:
        hint = " [y/n] "
    full_prompt = prompt.rstrip() + hint
    while True:
        answer = input(full_prompt).strip().lower()
        if not answer and default is not None:
            return default
        if answer in _YES:
            return True
        if answer in _NO:
            return False
        print("Please answer yes or no.")


def choice(prompt: str, options: Sequence[T]) -> T:
    """Show a numbered list of options and return the one picked.

    The user can type the number or the option's text.
    """
    if not options:
        raise ValueError("choice() needs at least one option.")
    option_list: List[T] = list(options)
    print(prompt)
    for number_, option in enumerate(option_list, start=1):
        print(f"  {number_}. {option}")
    while True:
        answer = input("> ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(option_list):
            return option_list[int(answer) - 1]
        for option in option_list:
            if str(option).lower() == answer.lower():
                return option
        print(f"Please type a number from 1 to {len(option_list)}, or one of the options.")


def password(prompt: str = "Password: ", confirm: bool = False, min_length: int = 0) -> str:
    """Ask for a password without showing what's typed.

    With confirm=True the user types it twice and must match.
    With min_length the password must be at least that many characters.
    """
    while True:
        answer = getpass.getpass(prompt)
        if not answer:
            print("Please type a password.")
            continue
        if len(answer) < min_length:
            print(f"Please use at least {min_length} characters.")
            continue
        if confirm and getpass.getpass("Type it again: ") != answer:
            print("The passwords didn't match. Let's try again.")
            continue
        return answer
