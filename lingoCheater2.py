import os
import pickle
import re
from collections import defaultdict, Counter
from copy import copy
from math import log
from random import choices

# VARIABLES

WORD_LEN = 5
MAX_GUESSES = 5

NUM_LOOPS = 10 ** 4

WORD_LIST_FILE = 'Collins Scrabble Words (2019).txt'
FREQ_LIST_FILE = 'all.num.o5.txt'
CACHE_FILE = 'cached.pickle'

# PROGRAM


def main():
    wl = WordList()

    # TODO: add a mode where human can play vs comp supplied words
    print(
        '1. [H]uman enters guesses and match strings from an external source\n',
        '2. [C]omputer plays vs itself',
        sep=''
    )
    while True:
        i = input('Choice?').lower()

        if i in ['1', 'h']:
            human_player(wl)
        elif i in ['2', 'c', '']:
            CompPlay(wl).cp_main()
            break
        else:
            print('Invalid Choice')


def human_player(wl):
    while True:
        first_letter = input('What\'s the first letter?').upper()

        pc = PossCalculator(wl, first_letter)

        while True:
            print('Best Guesses:')
            pc.print_best(5)

            guess = input('Guess?').upper()
            if guess == '':
                guess = first_letter + pc.get_best(1)[0][0]
                print(f'Guessing: {guess}')
            elif guess[1:] not in pc.poss:
                print(guess, 'is not a valid word. Please try again')
                continue

            match_string = input('Match String?').lower()
            if not re.search(r'[sox]{' + str(WORD_LEN) + '}', match_string):
                print('invalid match string. Please try again')

            num_poss = pc.calc_matches(guess, match_string)

            if num_poss == 1:
                print(f'  -={guess}=-')
                break

            print(f'  {num_poss} words left')

            if num_poss == 0:
                print('  WTF did you do?')
                break


def str_pos_sub(string, pos, sub):
    return string[:pos] + sub + string[pos + 1:]


class CompPlay:
    def __init__(self, wl):
        self.wl = wl

    def cp_main(self):
        guess_counter = Counter()
        for _ in range(NUM_LOOPS):
            word = self.get_word()[0]
            print(f'Word is: {word}')
            pc = PossCalculator(self.wl, word[0])

            guesses = []
            while True:
                guess = word[0] + pc.get_best(1)[0][0]
                if guess in guesses:
                    pc.poss.discard(guess[1:])
                    continue

                guesses.append(guess)

                if len(guesses) > MAX_GUESSES:
                    print('  :( too many guesses')
                    guess_counter['DQ'] += 1
                    break
                elif guess == word:
                    print(f'  -={word}=-')
                    print(f'   {len(guesses)} guesses')
                    guess_counter[len(guesses)] += 1
                    break

                match_string = self.get_match_string(word, guess)
                num_poss = pc.calc_matches(guess, match_string)

                print(f'    {guess}\t{match_string}\t{num_poss} words left')

                if word[1:] not in pc.poss:
                    print('  WTF did you do?')
                    guess_counter['WTF'] += 1
                    break

        print('\n')
        for guesses, count in guess_counter.most_common():
            print(f'{count:5d} solved in {guesses} guesses')

    def get_match_string(self, word, guess):
        match_string = '.' * WORD_LEN
        for pos in range(WORD_LEN):
            if guess[pos] == word[pos]:
                match_string = str_pos_sub(match_string, pos, 's')
                word = word.replace(word[pos], '.', 1)

        for pos in range(WORD_LEN):
            if match_string[pos] != '.':
                continue
            elif guess[pos] in word[1:]:
                match_string = str_pos_sub(match_string, pos, 'o')
                word = word.replace(guess[pos], '.', 1)
            else:
                match_string = str_pos_sub(match_string, pos, 'x')

        return match_string

    def get_word(self):
        return choices(
            list(self.wl.word_freq.keys()),  # population
            list(self.wl.word_freq.values()),  # weights  # TODO: speedup by turning this into a cached cumulative list
        )


class PossCalculator:
    def __init__(self, wl, first_letter):
        self.wl = wl
        self.first_letter = first_letter
        self.poss = copy(wl.starts_with(first_letter))
        print(f' starting letter {first_letter}, {len(self.poss)} words left')

    def calc_matches(self, guess, match_string):
        guess = guess[1:]
        match_string = match_string[1:]

        poss_copy = copy(self.poss)
        for word in poss_copy:
            if not self.check_valid(guess, match_string, word):
                self.poss.remove(word)

        return len(self.poss)

    def check_valid(self, guess, match_string, word):
        pos_dict = {
            's': [],
            'o': [],
            'x': [],
        }

        for pos, char in enumerate(match_string):
            pos_dict[char].append(pos)

        for pos in pos_dict['s']:
            if guess[pos] == word[pos]:
                word = str_pos_sub(word, pos, '.')
            else:
                return False

        for pos in pos_dict['o']:
            if guess[pos] in word and guess[pos] != word[pos]:
                word = word.replace(guess[pos], '.', 1)
            else:
                return False

        for pos in pos_dict['x']:
            if guess[pos] in word:
                return False

        # You have passed the three trials of the match_string. You have proven yourself.
        return True

    def get_best(self, n):
        char_score = Counter()
        for word in self.poss:
            for char in set(word):
                char_score[char] += 1

        word_scores = Counter()
        for word in self.poss:
            word_set = set(word)
            for char in word_set:
                word_scores[word] += char_score[char]

            word_scores[word] *= (len(word_set) + 1)

        avg_word_score = int(sum(word_scores.values()) / len(word_scores))

        for word, score in word_scores.items():
            word_scores[word] = int(score / avg_word_score * 130)
            word_scores[word] += self.wl.word_freq[self.first_letter + word]

        return word_scores.most_common(n)

    def print_best(self, n):
        for word, score in self.get_best(n):
            print(f'{self.first_letter}{word}\t{score}')


class WordList:
    def __init__(self):
        if os.path.exists(CACHE_FILE):
            print('Loading cached wordlist!')
            with open(CACHE_FILE, 'rb') as f:
                self.word_dict = pickle.load(f)
                self.word_freq = pickle.load(f)
        else:
            print('Building wordlist!')
            self.build_wordlists()

    def return_40(self):
        return 40   # pickle was failing when trying to pickle word_freq because of a lambda
                    # so I made this to be "not a lambda"

    def build_wordlists(self):

        self.word_dict = defaultdict(set)
        # word_dict is {first_letter: [rest_of_word1, rest_of_word2]}

        with open(WORD_LIST_FILE) as f:
            for word in f:
                if len(word) == WORD_LEN+1:
                    self.word_dict[word[0]].add(word[1:WORD_LEN])
                    # we already know the first letter, so cut off with [1:]
                    # there's a newline while reading, so cut it off with [:5]

        self.word_freq = defaultdict(self.return_40)

        with open(FREQ_LIST_FILE) as f:
            for line in f:
                line = line.split()
                if len(line[1]) == WORD_LEN:
                    word = line[1].upper()
                    if word[1:] in self.word_dict[word[0]]:
                        self.word_freq[word] = int(log(int(line[0]), 6) * 40)

        for word in self.word_freq:
            assert word[1:] in self.word_dict[word[0]]

        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(self.word_dict, f)
            pickle.dump(self.word_freq, f)

    def starts_with(self, first_letter):
        return self.word_dict[first_letter]


if __name__ == '__main__':
    main()
