from __future__ import annotations

from play_wordle.pick_word import WordPicker
from play_wordle.wordle_game import WordleGameAutomation


def main() -> int:
    game: WordleGameAutomation | None = None
    try:
        # Start Wordle game
        game = WordleGameAutomation(show_browser=True)
        word_picker = WordPicker()

        guess_feedback: list[list[str]] = []
        row_index = 0

        while not game.is_game_over(guess_feedback):
            guess = word_picker.choose_word(guess_feedback)
            if not guess:
                return 1
            game.enter_guess(guess, row_index)
            guess_feedback = game.read_game_feedback()
            row_index += 1

        # Copy share text
        results = game.collect_results()

        # Print the button text
        print(results)
    finally:
        # Closing the browser when done
        if game is not None:
            game.browser.close()
            game.p.stop()

    return 0
