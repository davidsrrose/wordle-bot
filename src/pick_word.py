import random
import time
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

class WordPicker:
    def __init__(self, word_list_file: str = "5_letter_words.txt"):
        self.word_list = self._read_word_list(word_list_file)
        self.possible_words = self.word_list
        logging.info("Word picker initialized...")

    def _read_word_list(self, word_list_file: str) -> list:
        """Reads in a list of all 5-letter words from a file."""
        with open(word_list_file, "r") as fin:
            return [line.strip().upper() for line in fin]

    def _parse_wordle_feedback(self, feedback: list[list]):
        """Parses feedback of colored tiles into constraint variables."""
        logging.info("Parsing feedback from game...")

        word_constraints = {
            "absent_letters": set(),
            "must_include": set(),
            "correct_positions": {},
            "disallowed_positions": {}
        }

        for row in feedback:
            # Skip rows with any "empty" feedback
            if any("empty" in item for item in row):
                continue

            for item in row:
                if "empty" in row:
                    continue

                position_descr, letter, info = item.split(", ")
                letter_position = int(position_descr.split()[0][:-2]) - 1

                if info == "absent":
                    word_constraints["absent_letters"].add(letter)

                elif info == "correct":
                    word_constraints["must_include"].add(letter)
                    word_constraints["correct_positions"][letter_position] = letter

                elif info == "present in another position":
                    word_constraints["must_include"].add(letter)
                    if letter not in word_constraints["disallowed_positions"]:
                        word_constraints["disallowed_positions"][letter] = set()
                    word_constraints["disallowed_positions"][letter].add(letter_position)

        return word_constraints

    def _is_valid_word(self, word: str, constraints: dict) -> bool:
        """ Checks if a word satisfies the given constraints. """

        must_include = constraints["must_include"]
        absent_letters = constraints["absent_letters"]
        correct_positions = constraints["correct_positions"]
        disallowed_positions = constraints["disallowed_positions"]
        
        # Ensure word contains all must_include letters
        for letter in must_include:
            if letter not in word:
                return False

        # Ensure word does not contain any absent_letters
        for letter in absent_letters:
            if letter in word:
                return False

        return True

    def _filter_word_list(self, feedback: list[list]) -> list:
        """Filters possible words based on feedback."""
        word_constraints = self._parse_wordle_feedback(feedback)

        filtered_words = []
        for word in self.possible_words:
            if self._is_valid_word(word, word_constraints):
                filtered_words.append(word)

        self.possible_words = filtered_words

        logging.info(f"{len(self.possible_words)} possible words...")
        
        return self.possible_words

    def choose_word(self, feedback: list[list]) -> str:
        """Chooses the next word to guess."""
        if not feedback:
            return "arson"  # Default first guess

        possible_words = self._filter_word_list(feedback)
        if possible_words:
            return random.choice(possible_words)
        else:
            logging.info("No valid words found...")

