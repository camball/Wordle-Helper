import json
import wordle


def main():
    with open("words_dictionary.json") as words:
        theDictionary: dict = json.load(words)

    for word in theDictionary:
        if len(word) != 5:
            continue

        #! Make sure to pass all lowercase letters! This could be changed, but would slow computation time.

        if wordle.allLettersInWordPositional(word, "?ar?a") and wordle.doesNotContain(
            word, "eoshkcnm"
        ):
            print(word)

        # if allLettersInWord(word, "clsh"):
        #     print(word)


if __name__ == "__main__":
    main()
