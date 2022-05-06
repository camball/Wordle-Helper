import json
import wordle
from functools import partial


def main():
    with open("words_dictionary.json") as words:
        theDictionary: dict = json.load(words)

    word_prototype = "?adge"

    found_words = list(
        filter(
            partial(wordle.doesNotContain, letters="rtoshcm"),
            filter(
                partial(wordle.allLettersInWordPositional, letters=word_prototype),
                filter(lambda word: len(word) == 5, theDictionary),
            ),
        )
    )
    # for word in found_words:
    #     print(word)
    for word in wordle.suggestWordsWithMaxInformation(found_words, word_prototype, 3):
        print(word)


if __name__ == "__main__":
    main()
