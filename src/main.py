from wordle_game import WordleGameAutomation
from pick_word import WordPicker

def main():

    # Start wordle game
    game = WordleGameAutomation(show_browser = True)
    word_picker = WordPicker()

    guess_feedback = []

    while not game.is_game_over(guess_feedback):
        guess = word_picker.choose_word(guess_feedback) 
        print(guess)
        game.enter_guess(guess)
        guess_feedback = game.read_game_feedback()

    # Closing the browser when done
    game.browser.close()
    game.p.stop()  # Stop Playwright context when done

if __name__ == "__main__":
    main()
