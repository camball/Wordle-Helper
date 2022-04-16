import json
from typing import Iterable


def allLettersInWord(letters: Iterable, word: str) -> bool:
    """A shorthand function for a bunch of `if \"c\" in word and \"b\" in word...`'s"""
    return all((letter in word for letter in letters))


def allLettersInWordPositional(letters: Iterable, word: str) -> bool:
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


def main():
    with open("words_dictionary.json") as words:
        theDictionary: dict = json.load(words)

    for word in theDictionary:
        if len(word) != 5:
            continue

        #! Make sure to pass all lowercase letters! This could be changed, but would slow computation time.

        if allLettersInWordPositional("n?l?n", word):
            print(word)

        # if allLettersInWord("clsh", word):
        #     print(word)


if __name__ == "__main__":
    main()
