import json
import wordle
from functools import partial


def main():
    with open("words_dictionary.json") as words:
        theDictionary: dict = json.load(words)

    found_words = filter(
        partial(wordle.doesNotContain, letters="eoshkcnm"),
        filter(
            partial(wordle.allLettersInWordPositional, letters="?ar?a"),
            filter(lambda word: len(word) == 5, theDictionary),
        ),
    )

    for word in found_words:
        print(word)


if __name__ == "__main__":
    main()
