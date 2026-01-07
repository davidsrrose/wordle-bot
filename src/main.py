from wordle_play_bot.pick_word import WordPicker
from wordle_play_bot.wordle_game import WordleGameAutomation


def main():
    # Start wordle game
    game = WordleGameAutomation(show_browser=True)
    word_picker = WordPicker()

    guess_feedback = []
    row_index = 0

    while not game.is_game_over(guess_feedback):
        guess = word_picker.choose_word(guess_feedback)
        game.enter_guess(guess, row_index)
        guess_feedback = game.read_game_feedback()
        row_index += 1

    # Copy share text
    results = game.collect_results()

    # Print the button text
    print(results)

    # Closing the browser when done
    game.browser.close()
    game.p.stop()  # Stop Playwright context when done


if __name__ == '__main__':
    main()
