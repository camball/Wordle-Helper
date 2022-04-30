"""A module with helper functions for solving Wordle puzzles.

Example usage:
```py
with open("words_dictionary.json") as words:
    theDictionary: dict = json.load(words)

for word in theDictionary:
    if len(word) != 5:
        continue

    if allLettersInWordPositional(word, "?ar?a") and doesNotContain(word, "eoshkcnm"):
        print(word)
```
"""

import json
from typing import Iterable


def allLettersInWord(word: str, letters: Iterable) -> bool:
    """A shorthand function for a bunch of `if \"c\" in word and \"b\" in word...`'s"""
    return all((letter in word for letter in letters))


def allLettersInWordPositional(word: str, letters: Iterable) -> bool:
    """A shorthand function for a bunch of `if word[0] == \"c\" and word[2] == \"b\"...`'s

    For any letter that you want to be "any" letter, use the '?' wildcard.
    For example, to search for any word containing \"y\" as the second letter
    and \"g\" as the fifth letter, pass \"?y??g\" to the `letters` argument.
    """
    try:
        for matchLetter, wordLetter in zip(letters, word, strict=True):
            if matchLetter == "?":
                continue

            if matchLetter != wordLetter:
                return False
    except ValueError:
        print(
            "Error: ensure that you have passed a `letters` argument of the same length as `word` to `allLettersInWordPositional()`"
        )
        exit()

    return True


def doesNotContain(word: str, letters: Iterable) -> bool:
    """If `word` does not contain any of the letters in `letters`, this returns True.
    Otherwise, this returns False.

    Useful for filtering out any letters that are known not to be in the word.
    """
    return False if any((letter in word for letter in letters)) else True


def main():
    with open("words_dictionary.json") as words:
        theDictionary: dict = json.load(words)

    for word in theDictionary:
        if len(word) != 5:
            continue

        #! Make sure to pass all lowercase letters! This could be changed, but would slow computation time.

        if allLettersInWordPositional(word, "?ar?a") and doesNotContain(
            word, "eoshkcnm"
        ):
            print(word)

        # if allLettersInWord(word, "clsh"):
        #     print(word)


if __name__ == "__main__":
    main()
