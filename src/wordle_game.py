import logging
import time
import random

from playwright.sync_api import sync_playwright

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

def human_like_delay(min_delay=0.5, max_delay=2.0):
    """Simulates a human-like delay between actions."""
    time.sleep(random.uniform(min_delay, max_delay))

class WordleGameAutomation:
    def __init__(self,show_browser) -> None:
        """Initializes the browser and opens the Wordle game."""
        logging.info("Starting wordle game...")
        self.p = sync_playwright().start()  # Start Playwright context
        self.browser = self.p.chromium.launch(headless = not show_browser)
        self.browser_context = self.browser.new_context( # a context with clipboard permissions
            permissions=["clipboard-read", "clipboard-write"]
        ) 
        self.page = self.browser_context.new_page()
        url = "https://www.nytimes.com/games/wordle/index.html"
        self.page.goto(url)
        self.close_popups()   
        self.turn_on_hard_mode()

    def close_popups(self) -> None:
        """Closes multiple popups in sequence."""
        self.page.click("text='Continue'")
        self.page.click("text='Play'")
        self.page.click("button[aria-label = 'Close']")
        logging.info("All popups closed...")

    def turn_on_hard_mode(self) -> None:
        """Enables hard mode in the settings."""

        # Open settings, turn on hard mode, close settings
        self.page.click('button[aria-label = "Settings"]')
        self.page.click('button[aria-label = "Hard Mode"]')
        self.page.click("button[aria-label = 'Close']")

        logging.info("Hard mode turned on...")

    def enter_guess(self, guess: str) -> None:
        human_like_delay()
        """Types a guess by simulating clicking on the on-screen keyboard."""
        logging.info(f"Guessing '{guess}'...")

        # Loop through each letter in the guess and click the corresponding key on the on-screen keyboard
        for letter in guess:
            letter_button = f"button[data-key='{letter.lower()}']" 
            # Wait for the button to be visible and click it
            self.page.wait_for_selector(letter_button, timeout=1000)
            self.page.click(letter_button)

        # After typing the guess, press Enter if needed to submit the guess
        self.page.click("button[aria-label = 'enter']")
        self.wait_for_any_animation_to_finish()

    def check_for_captcha(self):
        """Check if 'captcha' appears anywhere on the page."""
        page_content = self.page.content()  # Get the entire HTML content of the page
        if "captcha" in page_content.lower():  # Search for 'captcha' (case-insensitive)
            logging.info("Captcha detected on the page.")
            return True
        else:
            logging.info("No captcha detected on the page.")
            return False

    def wait_for_any_animation_to_finish(self):
        """Wait for all animations to finish and try clicking exit if it takes too long."""
        try:
            # Wait for any animations to finish on the current page
            self.page.wait_for_function('''() => {
                const elements = document.querySelectorAll('*');
                return !Array.from(elements).some(element => {
                    const style = window.getComputedStyle(element);
                    return style.animationName !== 'none' && style.animationDuration !== '0s';
                });
            }''', timeout=5000)  # Wait for up to 5 seconds
            
        except Exception as e:
            logging.warning("Animation took too long or failed to finish in time.")
            # If the wait exceeds 5 seconds or fails, try clicking the 'Exit' button
            # self.page.click("button[aria-label = 'Close']")

    def read_game_feedback(self) -> list:
        """Inspects the game tiles and returns a list of aria-labels for the tiles, structured by rows."""
        # Selector for tiles
        tile_selector = '[role="img"][aria-roledescription="tile"]'
        tiles = self.page.query_selector_all(tile_selector)

        # Collect aria-label values
        tile_feedback = [tile.get_attribute("aria-label") for tile in tiles]
        # Define the number of columns (Wordle is 5 columns per row)
        num_columns = 5

        # Split tile_feedback into rows
        rows = [
            tile_feedback[i:i + num_columns] 
            for i in range(0, len(tile_feedback), num_columns)
        ]
        # Return the rows directly without additional labels
        return rows

    def is_game_over(self,tile_feedback) -> bool:
        # Have not guessed yet
        if tile_feedback == []:
            return False    

        # Game won
        if self.is_game_win(tile_feedback):
            logging.info("Game won!")
            return True
        
        # Game lost
        if self.is_game_lost(tile_feedback):
            logging.info("Game lost :(")
            return True
        
        return False

    def is_game_lost(self, tile_feedback: list[list]) -> bool:
        """Checks if no rows in the tile feedback have 'empty'."""
        for row in tile_feedback:
            # Check if the row contains "empty" anywhere in the list
            if any("empty" in item for item in row):
                return False  # If any row has "empty", the game is not lost yet
            
        return True

    def is_game_win(self, tile_feedback: list[list]) -> bool:
        """Checks if any row in the tile feedback has all correct letters."""
        for row in tile_feedback:
            # Check if all items in the row are correct, this is a win
            if all("correct" in item for item in row):
                return True

        return False
    
    def screenshot_game(self) -> None:
        # take full page screenshot
        self.page.screenshot(path="full_page_screenshot.png")
    

    def get_share_button_content(self) -> str:

        # Click the share button to trigger the clipboard copy action
        self.page.click('button.Footer-module_shareButton__cHprS')

        # Wait a bit for the clipboard content to be copied (adjust the delay as needed)
        self.page.wait_for_timeout(500)

        # Retrieve the clipboard content via the browser context
        clipboard_content = self.page.evaluate('navigator.clipboard.readText()')

        return clipboard_content


