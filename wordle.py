"""A module with helper functions for solving Wordle puzzles.

Example usage:
```py
import wordle
import json

with open("words_dictionary.json") as words:
    theDictionary: dict = json.load(words)

for word in theDictionary:
    if len(word) != 5:
        continue

    if (
        wordle.allLettersInWordPositional(word, "?ar?a") and
        wordle.doesNotContain(word, "eoshkcnm")
    ):
        print("Found word:", word)
```

Make sure to pass all lowercase letters to the `letters` argument of all functions.
This could be fixed, but would slow computation time.
"""

from collections import Counter
from functools import partial
import json
from typing import Iterable
from sys import exit as sys_exit
from unittest import result


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
        sys_exit()

    return True


def doesNotContain(word: str, letters: Iterable) -> bool:
    """If `word` does not contain any of the letters in `letters`, this returns True.
    Otherwise, this returns False.

    Useful for filtering out any letters that are known not to be in the word.
    """
    return not any((letter in word for letter in letters))


def suggestWordsWithMaxInformation(
    word_list: list[str], positionalLetters: str, min_search_letters: int
):
    """
    Scans through `word_list`, and creates a distribution of the most frequent
    letters from each word. It then finds words from the dictionary that
    contain the as many of the most common letters as possible (minimum allowed
    amount specified by `min_search_letters`), and suggests words to play next
    that would maximise the amount of information you could get from a single
    word.

    The intended use for this function is to compute a list of words that the
    answer *could* be, by filtering out words from the dictionary using the
    information you already have (i.e., by calling `wordle.doesNotContain()`,
    etc.). Then, pass that filtered list to this function's `word_list`.

    `min_search_letters` must be on the interval [1,5]. You probably won't get
    useful results unless you use it with 3 or 4 though, as 5 will most likely
    yield no results as it is too restrictive, and 1 or 2 will likely yield too
    many results. However, trying 5 first may not be a bad idea because on the
    off chance that it does return a result, that would yield the highest
    amount of information.
    """
    unknown_letter_indices = [
        idx for idx, letter in enumerate(positionalLetters) if letter == "?"
    ]

    # a list of all the letters from words in word_list that could possibly be
    # in the ? positions. This list may (and is supposed to) contain duplicates.
    unknown_letters = [
        letter
        for word in word_list
        for idx, letter in enumerate(word)
        if idx in unknown_letter_indices
    ]

    with open("words_dictionary.json") as words:
        theDictionary: dict = json.load(words)
    len_five_words = list(filter(lambda word: len(word) == 5, theDictionary))

    most_common_letters = Counter(unknown_letters)

    top_n_letters = [
        letter for letter, _ in most_common_letters.most_common(min_search_letters)
    ]

    found_words = list(
        filter(
            partial(allLettersInWord, letters=top_n_letters),
            len_five_words,
        )
    )

    if not found_words:
        offset = 1  # initialise here, increment later if no results
        while min_search_letters + offset <= len(most_common_letters):
            # remove the least most common letter and see if adding the next
            # most common letter will give us any results
            top_n_letters.pop()
            top_n_letters.append(
                most_common_letters.most_common(min_search_letters + offset).pop()[0]
            )

            results = list(
                filter(
                    partial(allLettersInWord, letters=top_n_letters),
                    len_five_words,
                )
            )

            # if no results found, keep increment offset to search with next letter
            if not results:
                offset += 1
            else:
                found_words = results
                break

    return found_words
