Lingo is a game where the host secretly picks a 5 letter word, then provides the first letter to the player.
The player then guesses a word, and the host gives feedback on what letters are right, wrong, or in the wrong position.

I call this feedback match_string and use the following format:

's' = right letter, right position  (to represent square)

'o' = right letter, wrong position  (to represent circle)

'x' = letter is not in word.        (to represent.. well.. X)

This is a cheater for Lingo. It loads data from the word list (in this case scrabble dictionary) to find potential words.
It also provides guesses according to both the probability of characters in remaining words, and also an english word usage frequency.
