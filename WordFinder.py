from collections import defaultdict
from copy import copy

from pprint import pprint


MIN_LEN = 3


def main():
    wf = WordFinder()

    i = 'start'
    while i:
        i = input('letters?').upper()
        pprint(wf.get_words(i))


class WordFinder:
    def __init__(self):
        self.all_words = set()
        self.letter_sets = defaultdict(set)
        with open('Collins Scrabble Words (2019).txt') as f:
            for word in f:
                word = word.replace('\n', '')

                if word == 'Collins Scrabble Words (2019). 279,496 words. Words only.':
                    continue
                elif len(word) < MIN_LEN:
                    continue

                self.all_words.add(word)
                for char in word:
                    self.letter_sets[char].add(word)


    def get_words(self, letters):
        poss_words = copy(self.all_words)
        for char, char_set in self.letter_sets.items():
            if char not in letters:
                poss_words = poss_words - char_set

        for word in copy(poss_words):
            test_word = word
            for char in letters:
                test_word = test_word.replace(char, '.', 1)

            if set(test_word) != set('.'):
                poss_words.discard(word)

        return poss_words


if __name__ == '__main__':
    main()