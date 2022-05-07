import json
import wordle
from functools import partial


def main():
    theDictionary = wordle.getDictionary()

    word_prototype = "mi???"

    found_words = list(
        filter(
            partial(wordle.doesNotContain, letters="oarewngucy"),
            filter(
                partial(wordle.allLettersInWordPositional, letters=word_prototype),
                filter(
                    partial(wordle.allLettersInWord, letters="st"),
                    theDictionary,
                ),
            ),
        )
    )
    for word in found_words:
        print(word)
    # for word in wordle.suggestWordsWithMaxInformation(found_words, word_prototype, 4):
    #     print(word)


if __name__ == "__main__":
    main()
