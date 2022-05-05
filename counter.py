"""
This script takes in a list of words that the word possibly could be (i.e., the
output from `main.py`), gets the most common letters from the list, then gives
a list of the best possible words to play next to get the most information to
lead you to the right answer. Once you have played the word that this script
outputs, start at `main.py` all over again.
"""

from collections import Counter
from functools import partial
import json
import wordle

possible_words = [
    "dozer",
    "cover",
    "dozer",
    "hover",
    "joker",
    "loner",
    "lover",
    "lower",
    "mover",
    "mower",
    "poker",
    "power",
    "rover",
    "rower",
    "toner",
    "tower",
    "voter",
]

unknown_letters = []

for word in possible_words:
    unknown_letters.append(word[0])
    unknown_letters.append(word[2])

most_common_letters = Counter(unknown_letters)
top_n_letters = [letter for letter, _ in most_common_letters.most_common(3)]

with open("words_dictionary.json") as words:
    theDictionary: dict = json.load(words)

found_words = filter(
    partial(wordle.allLettersInWord, letters=top_n_letters),
    filter(lambda word: len(word) == 5, theDictionary),
)

for word in found_words:
    print(word)
