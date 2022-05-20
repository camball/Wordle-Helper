"""A module with helper functions for solving Wordle puzzles.

Example usage:
```py
import wordle

the_dictionary = wordle.get_dictionary()

for word in the_dictionary:
    if (
        wordle.all_letters_in_word_positional(word, "?ar?a") and
        wordle.does_not_contain(word, "eoshkcnm")
    ):
        print("Found word:", word)
```

Make sure to pass all lowercase letters to the `letters` argument of all functions.
This could be fixed, but would slow computation time.
"""

from collections import Counter
from functools import partial
from string import ascii_lowercase
import re
import json
from typing import Iterable, Sequence
from sys import exit as sys_exit

import inflect


def remove_plurals(word_list: Iterable) -> set[str]:
    """Remove all plural nouns from `word_list`. Powered by the `inflect` library."""
    inf = inflect.engine()
    # documentation is hard to understand for this function, so this was
    # written with the help of https://stackoverflow.com/a/39077936/
    return {word for word in word_list if not inf.singular_noun(word)}


def get_dictionary() -> set[str]:
    """Return a set of all 5-letter words."""
    with open("words_dictionary.json") as words:
        return set(filter(lambda word: len(word) == 5, json.load(words)))


def all_letters_in_word(word: str, letters: Iterable) -> bool:
    """A shorthand function for a bunch of `if \"c\" in word and \"b\" in word...`'s"""
    return all((letter in word for letter in letters))


def all_letters_in_word_positional(word: str, letters: Sequence) -> bool:
    """A shorthand function for a bunch of `if word[0] == \"c\" and word[2] == \"b\"...`'s

    For any letter that you want to be "any" letter, use the '?' wildcard.
    For example, to search for any word containing \"y\" as the second letter
    and \"g\" as the fifth letter, pass \"?y??g\" to the `letters` argument.
    """
    for matchLetter, wordLetter in zip(letters, word, strict=True):
        if matchLetter == "?":
            continue

        if matchLetter != wordLetter:
            return False

    return True


def does_not_contain(
    word: Sequence[str],
    lettersNotInWord: Iterable,
    knownCorrectPositions: Sequence[str] | None = None,
) -> bool:
    """Useful for filtering out any letters that are known not to be in the word.

    If `word` does not contain any of the letters in `letters`, this returns True.
    Otherwise, this returns False.

    If `knownCorrectPositions` is passed (i.e., not `None`), then this function
    only checks letter positions in the word that are unknown. For example, if
    the word "THOSE" is passed to `word` and the sequence "XXYGG" is passed to
    `knownCorrectPositions`, then only the letters ['T', 'H', 'O'] are
    considered in this function's logic. `knownCorrectPositions` expects the
    following syntax:
      - If the letter was GREY (not in the word), put X in the letter's position.
      - If the letter was YELLOW (somewhere in the word), put Y in the letter's position.
      - If the letter was GREEN (in the right spot in the word), put G in the letter's position.

    Passing `knownCorrectPositions` is useful for checking words that contain
    duplicates of the same letter, where in some places the letter is known to
    be in the correct position, but you know it doesn't contain any more
    instances of that letter throughout the word.
    """
    if knownCorrectPositions:
        word = [
            letter
            for letter, letterInfo in zip(word, knownCorrectPositions)
            if letterInfo == "?"
        ]

    return not any((letter in word for letter in lettersNotInWord))


# def noLettersInWrongSpotsThatAreInSameSpotsInWord(word: str, letters: Sequence) -> bool:
#     """My sincerest apologies for the abomination of a function name. It's 4:28
#     AM as I am coding this, and I had no idea what to call it. I've been coding
#     for four hours straight now, but I'm in too deep to stop so here we are.
#     I'm tired.
#     """
#     for matchLetter, wordLetter in zip(letters, word, strict=True):
#         if matchLetter == wordLetter:
#             return False
#         else:
#             continue

#     return True


def _filter_with_yellow_letters(
    word: str, yellow_letter_positions: dict[str, list[bool]]
) -> bool:
    """
    We want to filter out words that have any letter

    If `word` is "angry" and our dict is:
    {
        "a": [True, False, False, False, True]
        ...
    }
    then we should return False, because `word` contains a letter that has

    For each letter in the dictionary, checks if the location in `word` for that letter returns True.
    """
    # for dict_letter, places_letter_cannot_be in yellow_letter_positions.items():
    #     for word_letter, letter_is_yellow in zip(word, places_letter_cannot_be):
    #         if letter_is_yellow and dict_letter == word_letter:
    #             return False

    #     # if the letter isn't in the word at all... obviously return False
    #     if dict_letter not in word:
    #         return False

    # return True

    """
    The following implementation and the commented-out above implementation return the exact same results.
    I think the below one is a better implementation, though. It was the 2nd I wrote.
    """

    for yellow_letter, positions in yellow_letter_positions.items():
        for idx, letter in enumerate(word):
            if letter == yellow_letter and positions[idx] is True:
                return False

        # if the letter isn't in the word at all... obviously return False
        if yellow_letter not in word:
            return False

    return True


def _filter_with_yellow_letters_run_tests():
    words = ["angry", "alias", "super", "place", "house", "angse", "nasty"]

    yellow_letter_positions = {
        "a": [True, False, False, False, False],
        "s": [False, False, False, True, False],
    }

    for word in words:
        print(word, _filter_with_yellow_letters(word, yellow_letter_positions))


def suggest_words_with_max_information(
    word_list: list[str],
    green_letter_positions: Sequence[str],
    num_search_letters: int,
    positions_of_yellow_letters: dict[str, list[bool]] | None = None,
) -> list[str]:
    """
    Scans through `word_list`, and creates a distribution of the most frequent
    letters from each word. It then finds words from the dictionary that
    contain the as many of the most common letters as possible (minimum allowed
    amount specified by `num_search_letters`), and suggests words to play next
    that would maximise the amount of information you could get from a single
    word.

    The intended use for this function is to compute a list of words that the
    answer *could* be, by filtering out words from the dictionary using the
    information you already have (i.e., by calling `wordle.doesNotContain()`,
    etc.). Then, pass that filtered list to this function's `word_list`.

    `num_search_letters` must be on the interval [1,5]. You probably won't get
    useful results unless you use it with 3 or 4 though, as 5 will most likely
    yield no results as it is too restrictive, and 1 or 2 will likely yield too
    many results. However, trying 5 first may not be a bad idea because on the
    off chance that it does return a result, that would yield the highest
    amount of information.
    """

    """
    Compute most common letters from `word_list` that aren't already known.
    Say our word list is:
    - under
    - alias
    - class
    and `positionalLetters` is '?g??s'.

    Then this portion of this function will ignore the 1 and 4 indices, since we
    already know what's at those spots. It will take the letters from the 0, 2, 3
    spots of all words in `word_list` (i.e., {u,d,e,a,i,c,s}) and give us a Counter
    object which we use to get `num_search_letters` most common letters, which we
    store in `top_n_letters`.
    
    Those letters are used to filter the dictionary by, so we are only searching
    with the most likely guesses.
    """
    unknown_letter_indices = [
        idx for idx, letter in enumerate(green_letter_positions) if letter == "?"
    ]

    # a list of all the letters from words in word_list that could possibly be
    # in the ? positions. This list may (and is supposed to) contain duplicates.
    unknown_letters = [
        letter
        for word in word_list
        for idx, letter in enumerate(word)
        if idx in unknown_letter_indices
    ]

    THE_DICTIONARY = get_dictionary()

    most_common_letters = Counter(unknown_letters)

    top_n_letters = [
        letter for letter, _ in most_common_letters.most_common(num_search_letters)
    ]

    """
    Attempt to find suggestions by filtering the dictionary.
    """
    if positions_of_yellow_letters:
        found_words = list(
            filter(
                partial(
                    _filter_with_yellow_letters,
                    yellow_letter_positions=positions_of_yellow_letters,
                ),
                THE_DICTIONARY,
            )
        )
    else:
        found_words = list(
            filter(
                partial(all_letters_in_word, letters=top_n_letters),
                THE_DICTIONARY,
            )
        )

    """
    If no words were found, use a different set of letters and see if we get results that way.

    For example, if our top 3 most common letters are [r, n, k], but no results are
    returned, ditch the 'k' and move onto the next most common letter, searching with
    [r, n, t], for example.
    """
    if not found_words:
        offset = 1  # initialise here, increment later if no results
        while num_search_letters + offset <= len(most_common_letters):
            # remove the least most common letter and see if adding the next
            # most common letter will give us any results
            top_n_letters.pop()
            top_n_letters.append(
                most_common_letters.most_common(num_search_letters + offset).pop()[0]
            )

            if positions_of_yellow_letters:
                results = list(
                    filter(
                        partial(
                            _filter_with_yellow_letters,
                            yellow_letter_positions=positions_of_yellow_letters,
                        ),
                        THE_DICTIONARY,
                    )
                )
            else:
                results = list(
                    filter(
                        partial(all_letters_in_word, letters=top_n_letters),
                        THE_DICTIONARY,
                    )
                )

            # if no results found, keep increment offset to search with next letter
            if not results:
                offset += 1
            else:
                found_words = results
                break

        """
        If we STILL haven't found anything, recursively call this function,
        but with a less restrictive `num_search_letters`
        """
        if not found_words and num_search_letters - 1 > 0:
            found_words = suggest_words_with_max_information(
                word_list=word_list,
                green_letter_positions=green_letter_positions,
                num_search_letters=num_search_letters - 1,
                positions_of_yellow_letters=positions_of_yellow_letters,
            )
        """
        If we somehow still haven't found anything, as a last resort to return
        some sort of results, recursively return what this function would have
        returned had yellow letter positions not been passed.
        """
        if not found_words:
            found_words = suggest_words_with_max_information(
                word_list=word_list,
                green_letter_positions=green_letter_positions,
                num_search_letters=num_search_letters,
                positions_of_yellow_letters=None,
            )

    return found_words


class Wordle:
    """ """

    """
    removePlurals reduces possible words from 15918 to 12735. Nice!
    when suggesting words that we think are the correct words, we never want to
    suggest a plural, as those will never be correct. However, when there is
    not enough information to try and solve the Wordle, we DON'T filter out
    plurals (i.e., in suggestWordsWithMaxInformation()), so that we can suggest
    the best possible guess, whether it would be a winner or not.
    """
    THE_DICTIONARY = remove_plurals(get_dictionary())

    _found_words_threshold = 30

    def __init__(self) -> None:
        self._letters_not_in_word = set()
        self._green_letter_positions = ["?", "?", "?", "?", "?"]
        self._yellow_letter_positions: dict[str, list[bool]] = {
            letter: [False] * 5 for letter in ascii_lowercase
        }
        """
        This instance var can be tricky to understand, so here's an attempt at
        an explanation. Every letter in the alphabet can be discovered to not
        be in the word in multiple positions (but be in the word *somewhere*),
        so we need a way to represent the positions that *each letter* is known
        not to be in. It's best to see an example. If this argument is set to:
        {
            "a": [True, False, False, True, False],
            "b": [False, False, False, False, True],
            ...
        }
        then this means that "we know the letter 'a' is NOT in the 0th or 4th
        positions, and we know the letter 'b' is NOT in the 0th-3rd positions.

        In other words, when the value is set to `True` for a given position,
        we know the letter is somewhere in the word-just not at that position.
        """

    @staticmethod
    def _yellow_letter_positions_to_set(
        yellow_letter_positions: dict[str, list[bool]],
    ) -> set[str]:
        return {
            letter
            for letter, positions in yellow_letter_positions.items()
            if any(positions)
        }

    @staticmethod
    def _info_has_invalid_chars(information: str) -> bool:
        for char in information:
            if char.upper() not in {"X", "Y", "G"}:
                return True

        return False

    @staticmethod
    def _process_input(
        word_played: str, information: str
    ) -> tuple[set[str], list[str], list[str]]:
        """
        Take in the word that was played and the Grey, Yellow, and Green information
        about the word, and return a tuple containing:
        1. The letters that are not in the word,
        2. The letters that are in the word, but are in the wrong spots, and
        3. The letters that are known to be in specific places in the word

        This function can be tuple-unpacked as input to the `Wordle._updateWordInformation()` method.
        """
        letters_not_in_word = set()
        yellow_letter_positions = ["?", "?", "?", "?", "?"]
        green_letter_positions = ["?", "?", "?", "?", "?"]

        # Don't need to check for arg lengths to be the same. Arguments checked beforehand.
        for idx, (letter, letterInfo) in enumerate(zip(word_played, information)):
            letterInfo = letterInfo.upper()
            if letterInfo == "X":
                letters_not_in_word.add(letter)
            elif letterInfo == "Y":
                yellow_letter_positions[idx] = letter
            elif letterInfo == "G":
                green_letter_positions[idx] = letter

        return letters_not_in_word, yellow_letter_positions, green_letter_positions

    def _update_word_information(
        self,
        letters_not_in_word: set[str],
        yellow_letter_positions: Sequence[str],
        green_letter_positions: Sequence[str],
    ):
        """Update the internal representation of the known information about
        the word with any new information that has been found out. This function
        has three jobs:
        1. Union `letters_not_in_word` with `self._letters_not_in_word`
        2. Use `yellow_letter_positions` to update `self._yellow_letter_positions`, and remove any letters discovered positionally
        3. Merge `green_letter_positions` with `self._green_letter_positions`
        """

        # update letters not in word
        self._letters_not_in_word = self._letters_not_in_word | letters_not_in_word

        # update letters in word in wrong spots
        for idx, letter in enumerate(yellow_letter_positions):
            if letter != "?":
                self._yellow_letter_positions[letter][idx] = True

        # update letters in word with known position
        for idx, letter in enumerate(green_letter_positions):
            if letter != "?":
                self._green_letter_positions[idx] = letter

        # if we discover a known-position letter, take it out of the letters-in-wrong-spots list
        for idx, letter in enumerate(self._green_letter_positions):
            if letter != "?":
                # This will never throw KeyError/is safe. We are always passing
                # a letter from ascii_lowercase and the dictionary always
                # contains all of ascii_lowercase as keys.
                self._yellow_letter_positions[letter][idx] = True

    def play(self) -> None:
        print(
            "First, it is recommended to play the word SOARE, but you can play whatever you would like.\n"
        )

        while True:
            # process user input
            while True:
                wordPlayed = input(
                    "Enter the word you played (or 'Q' to quit): "
                ).lower()
                print("")
                if wordPlayed.upper() == "Q":
                    return
                elif len(wordPlayed) != 5:
                    print("Invalid input. Ensure your word is five characters.")
                    continue
                else:
                    break

            while True:
                information = input(
                    "Enter the information you received following the format described in the instructions: "
                )
                print("")
                if len(information) != 5:
                    print(
                        "Invalid input. Ensure your word information is five characters."
                    )
                    continue
                elif Wordle._info_has_invalid_chars(information):
                    print(
                        "Invalid input. Word information can only contain charactes 'X', 'Y', and 'G'."
                    )
                else:
                    break

            # update internal word knowledge to ultimately filter dictionary with
            self._update_word_information(
                *Wordle._process_input(wordPlayed, information)
            )

            # compute most likely words for user
            found_words = list(
                filter(  # filter out all words that contain letters in the "not in word" list (in the non-positional spots)
                    partial(
                        does_not_contain,
                        lettersNotInWord=self._letters_not_in_word,
                        knownCorrectPositions=self._green_letter_positions,
                    ),
                    filter(  # filter out all words that don't match the positional letter prototype
                        partial(
                            all_letters_in_word_positional,
                            letters=self._green_letter_positions,
                        ),
                        filter(  # filter out all words that don't have all the yellow letters
                            partial(
                                all_letters_in_word,
                                letters=Wordle._yellow_letter_positions_to_set(
                                    self._yellow_letter_positions
                                ),
                            ),
                            Wordle.THE_DICTIONARY,
                        ),
                    ),
                )
            )

            # present findings to the user
            if len(found_words) > Wordle._found_words_threshold:
                print(
                    f"Not enough information currently; more than {Wordle._found_words_threshold} results found."
                )
                print(
                    """You should instead play one of the following words to get
the most information out of the next word:\n"""
                )

                word_suggestions = suggest_words_with_max_information(
                    word_list=found_words,
                    green_letter_positions=self._green_letter_positions,
                    num_search_letters=5,
                    positions_of_yellow_letters=self._yellow_letter_positions,
                )

                # only return the top ten results
                for idx, word in enumerate(word_suggestions[:10]):
                    print(f"{idx + 1}. {word}")
                print("")
            elif len(found_words) == 0:
                print(
                    "No words found... hm... play something of your choice, I guess...\n"
                )
            else:
                print(
                    """The following words were found. Recall that most of the
time, common words are more likely to be the answer than very odd words.\n"""
                )

                for word in found_words:
                    print(word)

                print("")


def _word_finder():
    theDictionary = get_dictionary()

    while True:
        resp = input("Filter plurals from results? [Y/n]: ")[0].upper()
        if resp != "Y" and resp != "N":
            print("Please enter a valid response... [y/n]")
        else:
            if resp == "Y":
                theDictionary = remove_plurals(theDictionary)
            break

    positionalLetterCheck = re.compile(r"^[a-z?]{5}$")
    while True:
        word_prototype = input(
            'Enter green letters, with unknown letters as questions marks (e.g., "ap??e"): '
        ).lower()
        if not positionalLetterCheck.match(word_prototype):
            print(
                "Please ensure your response only contains letters and/or question marks..."
            )
        else:
            break

    normalLetterCheck = re.compile(r"^[a-z]*$")
    while True:
        letters = input('Enter yellow letters (e.g., "rpi"): ').lower()
        if not normalLetterCheck.match(letters):
            print("Please ensure your response only contains letters...")
        else:
            break

    while True:
        lettersNotInWord = input('Enter grey letters (e.g., "qpgt"): ').lower()
        if not normalLetterCheck.match(lettersNotInWord):
            print("Please ensure your response only contains letters...")
        else:
            break

    found_words = list(
        filter(
            partial(does_not_contain, lettersNotInWord=lettersNotInWord),
            filter(
                partial(all_letters_in_word_positional, letters=word_prototype),
                filter(
                    partial(all_letters_in_word, letters=letters),
                    theDictionary,
                ),
            ),
        )
    )

    print(
        """\nThe following words were found. Recall that most of the time,
common words are more likely to be the answer than very odd words.\n"""
    )

    for word in found_words:
        print(word)

    print("")


def _print_menu(options: dict[str, str]):
    for k, v in options.items():
        print(
            "{k:<{maxKeyLen}} : {v:>4}".format(
                k=k, maxKeyLen=max(len(k) for k in options), v=v
            )
        )
    print("")


def _print_instructions():
    print(
        """For interactive WORDLE solver mode, enter 'P' at the menu.
For an advanced word finder mode to help with individual WORDLE steps, enter 'A' at the menu.

--- Interactive Mode Instructions ---
1. Each round, you will be provided with a word (or multiple word options) to play from.
2. Play a word in WORDLE.
3. Follow the prompts to enter the letter information you received from the word you played.
    - First, enter the word you played
    - Second, enter a string of characters corresponding to the information you got back.
        - If the letter was GREY (not in the word), enter X in the letter's position.
        - If the letter was YELLOW (somewhere in the word), enter Y in the letter's position.
        - If the letter was GREEN (in the right spot in the word), enter G in the letter's position.
    
    For example, if you play the word GHOST, and 
        - the G, H, and T are not in the word (i.e., in grey),
        - the O is in the word (i.e., in yellow), and
        - the S is in the word in the right place (i.e., in green),
    then enter the string "XXYGX"

4. Repeat this process until the game is over.\n"""
    )


def _print_credits():
    print("This program © 2022 Cameron Ball. All rights reserved.\n")


def main():
    print("Welcome to the WORDLE solver!\n")

    menu_options = {
        "Instructions": "I",
        "Play Game": "P",
        "Advanced Word Finder Mode": "A",
        "Credits": "C",
        "Quit": "Q",
    }

    _print_menu(menu_options)
    while True:
        cmd = input("> ").upper()
        print("")
        if cmd not in menu_options.values():
            print("Invalid option. Valid options include:")
            _print_menu(menu_options)
        elif cmd == "I":
            _print_instructions()
        elif cmd == "A":
            _word_finder()
        elif cmd == "P":
            game = Wordle()
            game.play()
            print("[Game ended]\n")
        elif cmd == "C":
            _print_credits()
        elif cmd == "Q":
            break

    print("Thanks for playing!")


if __name__ == "__main__":
    main()
