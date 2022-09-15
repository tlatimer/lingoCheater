import random

SCRABBLE_WORDS_FILE = 'Collins Scrabble Words (2019).txt'
COMP_VS_COMP_GAMES = 100


def main():
    word_db = WordDB()
    while True:
        # i = input('First Letter?').upper()  # TODO: put back to manual mode
        pass


def main_comp_vs_comp():
    word_db = WordDB()

    num_games = COMP_VS_COMP_GAMES
    while num_games > 0:
        num_games -= 1

        secret_word = random.choices(word_db.all_words)

        word_comp = WordCompare(word_db.get_initial_words(secret_word[0]))

        raise hell  # force to debugger


class WordCompare:
    def __init__(self, initial_possibilities):
        self.poss = initial_possibilities

    def get_feedback(self, secret_word, guess):
        """The core algorithm of this whole thing"""
        return 'sxxxx'

    def apply_feedback(self, guess, feedback):
        for poss in self.poss:
            is_possible = self.get_feedback(guess, poss) == feedback
            if not is_possible:
                self.poss.remove(poss)

        assert len(self.poss) > 0  # this was the issue with the old version

    # def is_possible(self, orig_guess, feedback, new_guess):
    #     return self.get_feedback(orig_guess, new_guess) == feedback


class WordDB:
    def __init__(self):
        self.all_words = self._legal_words()

    def get_initial_words(self, first_letter):
        return set([x for x in self.all_words if x.startswith(first_letter)])

    @staticmethod
    def _legal_words(filename=SCRABBLE_WORDS_FILE, letters=5):
        legal_words = set()
        with open(filename) as f:
            for word in f.readlines():
                if len(word) == letters + 1:  # newline is counted as a character
                    legal_words.add(word[:-1])
        return legal_words


if __name__ == '__main__':
    main_comp_vs_comp()
