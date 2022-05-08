"""A module with helper functions for solving Wordle puzzles.

Example usage:
```py
import wordle
import json

with open("words_dictionary.json") as words:
    the_dictionary: dict = json.load(words)

for word in the_dictionary:
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
from typing import Iterable, Sequence
from sys import exit as sys_exit


def getDictionary() -> set[str]:
    with open("words_dictionary.json") as words:
        return set(filter(lambda word: len(word) == 5, json.load(words)))


def allLettersInWord(word: str, letters: Iterable) -> bool:
    """A shorthand function for a bunch of `if \"c\" in word and \"b\" in word...`'s"""
    return all((letter in word for letter in letters))


def allLettersInWordPositional(word: str, letters: Sequence) -> bool:
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
            """Error: ensure that you have passed a `letters` argument of the 
same length as `word` to `allLettersInWordPositional()`"""
        )
        sys_exit()

    return True


def doesNotContain(word: str, letters: Iterable) -> bool:
    """If `word` does not contain any of the letters in `letters`, this returns True.
    Otherwise, this returns False.

    Useful for filtering out any letters that are known not to be in the word.
    """
    return not any((letter in word for letter in letters))


def noLettersInWrongSpotsThatAreInSameSpotsInWord(word: str, letters: Sequence) -> bool:
    """My sincerest apologies for the abomination of a function name. It's 4:28
    AM as I am coding this, and I had no idea what to call it. I've been coding
    for four hours straight now, but I'm in too deep to stop so here we are.
    I'm tired.
    """
    try:
        for matchLetter, wordLetter in zip(letters, word, strict=True):
            if matchLetter == wordLetter:
                return False
            else:
                continue

    except ValueError:
        print(
            """Error: ensure that you have passed a `letters` argument of the 
same length as `word` to `allLettersInWordPositional()`"""
        )
        sys_exit()

    return True


def suggestWordsWithMaxInformation(
    word_list: list[str],
    positionalLetters: Sequence[str],
    min_search_letters: int,
    positionsOfLettersInWrongSpots: Sequence[str] | None = None,
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

    If a value is passed to `positionsOfLettersInWrongSpots`, this function
    will use those values to better reduce `word_list`. The value passed to
    this argument should be five characters long and of the form "?F??R", for
    example. In that example, the syntax means "F is in the word, but it's not
    in the 2nd spot, and R is in the word, but it's not in the 5th spot." If
    nothing is passed, this functionality is ignored. The philosophy behind
    this argument's existence is that if we have a letter that we know is in
    the word, but not where it is in the word, we don't want to play a word
    that has the letter in that same spot; we want to try a new spot to try and
    discover a positional letter.

    Functionality that may make it into this function at a future date:
    If a value is passed to this argument (positionsOfLettersInWrongSpots) and
    no results are returned, this function resorts to how it would function as
    if nothing was passed to this argument as a last-chance attempt to return
    some sort of results.
    """
    if positionsOfLettersInWrongSpots and len(positionsOfLettersInWrongSpots) != 5:
        raise ValueError(
            "argument `positionsOfLettersInWrongSpots` must be of length 5."
        )

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

    len_five_words = getDictionary()

    most_common_letters = Counter(unknown_letters)

    top_n_letters = [
        letter for letter, _ in most_common_letters.most_common(min_search_letters)
    ]

    if positionsOfLettersInWrongSpots:
        found_words = list(
            filter(
                partial(
                    noLettersInWrongSpotsThatAreInSameSpotsInWord,
                    letters=positionsOfLettersInWrongSpots,
                ),
                filter(
                    partial(allLettersInWord, letters=top_n_letters),
                    len_five_words,
                ),
            )
        )
    else:
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

            if positionsOfLettersInWrongSpots:
                results = list(
                    filter(
                        partial(
                            noLettersInWrongSpotsThatAreInSameSpotsInWord,
                            letters=positionsOfLettersInWrongSpots,
                        ),
                        filter(
                            partial(allLettersInWord, letters=top_n_letters),
                            len_five_words,
                        ),
                    )
                )
            else:
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


class Wordle:
    THE_DICTIONARY = getDictionary()
    _found_words_threshold = 30

    @staticmethod
    def _lettersInWordInWrongSpotsToSet(
        positionsOfLettersInWrongSpots: Sequence[str],
    ) -> set[str]:
        return {char for char in positionsOfLettersInWrongSpots if char != "?"}

    @staticmethod
    def _infoHasInvalidCharacters(information: str) -> bool:
        for char in information:
            if char.upper() not in {"X", "Y", "G"}:
                return True

        return False

    @staticmethod
    def _processInput(wordPlayed: str, information: str) -> tuple[set, list, list]:
        """
        Take in the word that was played and the Grey, Yellow, and Green information
        about the word, and return a tuple containing:
        1. The letters that are not in the word,
        2. The letters that are in the word, but are in the wrong spots, and
        3. The letters that are known to be in specific places in the word

        This function can be tuple-unpacked as input to the `Wordle._updateWordInformation()` method.
        """
        lettersNotInWord = set()
        lettersInWordInWrongSpots = ["?", "?", "?", "?", "?"]
        lettersInWordPositional = ["?", "?", "?", "?", "?"]

        # Don't need to check for arg lengths to be the same. Arguments checked beforehand.
        for idx, (letter, letterInfo) in enumerate(zip(wordPlayed, information)):
            letterInfo = letterInfo.upper()
            if letterInfo == "X":
                lettersNotInWord.add(letter)
            elif letterInfo == "Y":
                lettersInWordInWrongSpots[idx] = letter
            elif letterInfo == "G":
                lettersInWordPositional[idx] = letter

        return lettersNotInWord, lettersInWordInWrongSpots, lettersInWordPositional

    def __init__(self) -> None:
        self._letters_not_in_word = set()
        self._letters_in_word_positional = ["?", "?", "?", "?", "?"]
        self._letters_in_word_in_wrong_spots = ["?", "?", "?", "?", "?"]

    def _updateWordInformation(
        self,
        lettersNotInWord: set,
        lettersInWordInWrongSpots: list,
        lettersInWordPositional: list,
    ):
        """Update the internal representation of the known information about
        the word with any new information that has been found out. This function
        has three jobs:
        1. Union `lettersNotInWord` with `self._letters_not_in_word`
        2. Union `lettersInWord` with `self._letters_in_word`, and remove any letters discovered positionally
        3. Merge `lettersInWordPositional` with `self._letters_in_word_positional`
        """

        # update letters not in word
        self._letters_not_in_word = self._letters_not_in_word | lettersNotInWord

        # update letters in word in wrong spots
        for idx, letter in enumerate(lettersInWordInWrongSpots):
            if letter != "?":
                self._letters_in_word_in_wrong_spots[idx] = letter

        # update letters in word with known position
        for idx, letter in enumerate(lettersInWordPositional):
            if letter != "?":
                self._letters_in_word_positional[idx] = letter

        # if we discover a known-position letter, take it out of the letters-in-wrong-spots list
        for idx, (positionalLetter, wrongSpotLetter) in enumerate(
            zip(self._letters_in_word_positional, self._letters_in_word_in_wrong_spots)
        ):
            if positionalLetter != "?":
                self._letters_in_word_in_wrong_spots[idx] = "?"

    def play(self) -> None:
        # always play SOARE first
        print("First, play the word: SOARE\n")

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
                elif Wordle._infoHasInvalidCharacters(information):
                    print(
                        "Invalid input. Word information can only contain charactes 'X', 'Y', and 'G'."
                    )
                else:
                    break

            # update internal word knowledge to ultimately filter dictionary with
            self._updateWordInformation(*Wordle._processInput(wordPlayed, information))

            # compute most likely words for user
            found_words = list(
                filter(
                    partial(doesNotContain, letters=self._letters_not_in_word),
                    filter(
                        partial(
                            allLettersInWordPositional,
                            letters=self._letters_in_word_positional,
                        ),
                        filter(
                            partial(
                                allLettersInWord,
                                letters=Wordle._lettersInWordInWrongSpotsToSet(
                                    self._letters_in_word_in_wrong_spots
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

                word_suggestions = suggestWordsWithMaxInformation(
                    word_list=found_words,
                    positionalLetters=self._letters_in_word_positional,
                    min_search_letters=4,
                    positionsOfLettersInWrongSpots=self._letters_in_word_in_wrong_spots,
                )

                # only return the top five results
                for idx, word in enumerate(word_suggestions[:5]):
                    print(f"{idx + 1}. {word}")
                print("")
            elif len(found_words) == 0:
                print(
                    "No words found... hm... play something of your choice, I guess...\n"
                )
            else:
                print(
                    """The following words were found. Recall that WORDLE never
uses plural words (i.e., "trees") as the answer. Also
recall that most of the time, common words are more likely
to be the answer than very odd words.\n"""
                )

                for word in found_words:
                    print(word)

                print("")


def _printMenu(options: dict[str, str]):
    for k, v in options.items():
        print(
            "{k:<{maxKeyLen}} : {v:>4}".format(
                k=k, maxKeyLen=max(len(k) for k in options), v=v
            )
        )
    print("")


def _printInstructions():
    print(
        """1. Each round, you will be provided with a word (or multiple word options) to play from.
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


def _printCredits():
    print("This program © 2022 Cameron Ball. All rights reserved.\n")


def main():
    print("Welcome to the WORDLE solver!\n")

    menu_options = {"Instructions": "I", "Play Game": "P", "Credits": "C", "Quit": "Q"}

    _printMenu(menu_options)
    while True:
        cmd = input("> ").upper()
        print("")
        if cmd not in menu_options.values():
            print("Invalid option. Valid options include:")
            _printMenu(menu_options)
        elif cmd == "I":
            _printInstructions()
        elif cmd == "P":
            game = Wordle()
            game.play()
            print("[Game ended]\n")
        elif cmd == "C":
            _printCredits()
        elif cmd == "Q":
            break

    print("Thanks for playing!")


if __name__ == "__main__":
    main()
