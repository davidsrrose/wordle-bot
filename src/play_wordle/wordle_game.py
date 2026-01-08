import random
import time

from loguru import logger
from playwright.sync_api import BrowserContext, Page, sync_playwright


def human_like_delay(min_delay=0.5, max_delay=2.0):
    """Simulates a human-like delay between actions."""
    time.sleep(random.uniform(min_delay, max_delay))


class WordleGameAutomation:
    def __init__(self, show_browser: bool = True) -> None:
        """Initializes the browser and opens the Wordle game."""
        logger.info('Starting wordle game...')
        self.p = sync_playwright().start()  # Start Playwright context
        self.browser = self.p.chromium.launch(headless=not show_browser)
        self.browser_context: BrowserContext = self.browser.new_context(  # a context with clipboard permissions
            permissions=['clipboard-read', 'clipboard-write']
        )
        self.page = self.browser_context.new_page()
        self.page.set_default_navigation_timeout(60_000)
        self.page.set_default_timeout(15_000)
        self.ensure_ready()

    # --- Helpers ---
    def _handle_new_page(self, page: Page) -> None:
        """Close unexpected popups/tabs that navigate away from Wordle."""
        try:
            page.wait_for_load_state('domcontentloaded', timeout=3_000)
            url = page.url
            # Ignore the main page, blank pages, or pages without an opener (likely the main tab).
            if page == self.page or url in ('about:blank', '') or page.opener is None:
                return

            if 'nytimes.com/games/wordle' not in url:
                logger.warning(f'Closing unexpected popup/tab: {url}')
                page.close()
        except Exception:
            try:
                page.close()
            except Exception:
                pass

    def click_button(self, name: str, role: str = 'button', timeout_ms: int = 5_000, retries: int = 1) -> bool:
        """Click a button by role/name with limited retries; returns True if clicked."""
        for attempt in range(retries + 1):
            try:
                self.page.get_by_role(role, name=name).click(timeout=timeout_ms)
                return True
            except Exception:
                if attempt >= retries:
                    return False
                self.page.wait_for_timeout(300)  # brief settle before retry
        return False

    def wait_for_keyboard_ready(self, timeout_ms: int = 10_000) -> None:
        """Wait until the on-screen keyboard Enter key is present (board loaded)."""
        self.page.wait_for_selector("button[aria-label = 'enter']", timeout=timeout_ms)

    def ensure_ready(self) -> None:
        """Navigate, close intro popups, toggle hard mode, and confirm the board is ready."""
        url = 'https://www.nytimes.com/games/wordle/index.html'
        self.page.goto(url, wait_until='load', timeout=60_000)
        self.close_popups()
        self.wait_for_keyboard_ready()
        self.turn_on_hard_mode()

    def close_popups(self) -> None:
        """Closes multiple popups in sequence."""
        # Try to click the Play CTA first; wait explicitly for it to appear.
        try:
            self.page.wait_for_selector("button:has-text('Play')", timeout=8_000)
            self.page.locator("button:has-text('Play')").click(timeout=3_000)
            logger.info('Clicked Play CTA.')
        except Exception:
            logger.debug('Play button not found; continuing.')

        # Close any intro modal if present.
        clicked_close = self.click_button('Close', timeout_ms=3_000)
        if not clicked_close:
            logger.debug('Intro popup already closed.')

        logger.info('All popups closed (or already absent)...')

    def turn_on_hard_mode(self) -> None:
        """Enables hard mode in the settings."""

        try:
            if not self.click_button('Settings', timeout_ms=5_000):
                logger.warning('Settings button not found; continuing in normal mode.')
                return

            toggle = self.page.get_by_role('switch', name='Hard Mode')
            state = toggle.get_attribute('aria-checked')
            if state != 'true':
                toggle.click(timeout=3_000)
                logger.info('Hard mode toggled on.')
            else:
                logger.info('Hard mode already on.')

            self.click_button('Close', timeout_ms=3_000)
        except Exception:
            logger.warning('Hard mode toggle not found; continuing in normal mode.')

    def enter_guess(self, guess: str, row_index: int) -> None:
        """Types a guess by simulating clicking on the on-screen keyboard."""
        human_like_delay()
        logger.info(f"Guessing '{guess}'...")

        for letter in guess:
            letter_button = f"button[data-key='{letter.lower()}']"
            self.page.wait_for_selector(letter_button, timeout=1_000)
            self.page.click(letter_button)

        self.page.click("button[aria-label = 'enter']")
        self.wait_for_row_to_settle(row_index)

    def check_for_captcha(self) -> bool:
        """Check if 'captcha' appears anywhere on the page."""
        page_content = self.page.content()  # Get the entire HTML content of the page
        if 'captcha' in page_content.lower():  # Search for 'captcha' (case-insensitive)
            logger.info('Captcha detected on the page.')
            return True
        else:
            logger.info('No captcha detected on the page.')
            return False

    def wait_for_row_to_settle(self, row_index: int, timeout_ms: int = 10_000) -> None:
        """Wait until the given row has 5 evaluated tiles and is stable."""
        row_target = (row_index + 1) * 5
        self.page.wait_for_function(
            """(rowTarget) => {
                const tiles = Array.from(document.querySelectorAll('[role="img"][aria-roledescription="tile"]'));
                const evaluated = tiles.filter(t => {
                    const label = t.getAttribute('aria-label') || '';
                    return label.includes('correct') || label.includes('present') || label.includes('absent');
                });
                return evaluated.length >= rowTarget;
            }""",
            arg=row_target,
            timeout=timeout_ms,
        )
        # Brief settle to avoid flakiness on rapid updates.
        self.page.wait_for_timeout(200)

    def read_game_feedback(self) -> list:
        """Inspects the game tiles and returns a list of aria-labels for the tiles, structured by rows."""
        # Selector for tiles
        tile_selector = '[role="img"][aria-roledescription="tile"]'
        tiles = self.page.query_selector_all(tile_selector)

        # Collect aria-label values
        tile_feedback = [tile.get_attribute('aria-label') for tile in tiles]
        # Define the number of columns (Wordle is 5 columns per row)
        num_columns = 5

        # Split tile_feedback into rows
        rows = [tile_feedback[i : i + num_columns] for i in range(0, len(tile_feedback), num_columns)]
        # Return the rows directly without additional labels
        return rows

    def is_game_over(self, tile_feedback) -> bool:
        # Have not guessed yet
        if tile_feedback == []:
            return False

        # Game won
        if self.is_game_win(tile_feedback):
            logger.info('Game won!')
            return True

        # Game lost
        if self.is_game_lost(tile_feedback):
            logger.info('Game lost :(')
            return True

        return False

    def is_game_lost(self, tile_feedback: list[list]) -> bool:
        """Checks if no rows in the tile feedback have 'empty'."""
        for row in tile_feedback:
            # Check if the row contains "empty" anywhere in the list
            if any('empty' in item for item in row):
                return False  # If any row has "empty", the game is not lost yet

        return True

    def is_game_win(self, tile_feedback: list[list]) -> bool:
        """Checks if any row in the tile feedback has all correct letters."""
        for row in tile_feedback:
            # Check if all items in the row are correct, this is a win
            if all('correct' in item for item in row):
                return True

        return False

    def screenshot_game(self) -> None:
        # take full page screenshot
        self.page.screenshot(path='full_page_screenshot.png')

    def collect_results(self) -> str:
        """Open results/share flow, copy the result text, and return it."""

        # Close any win modal that blocks the underlying board/share button.
        self.click_button('Close', timeout_ms=2_000)

        # If a "See results" button is present (post-win screen), click it to reveal share.
        self.click_button('See results', timeout_ms=3_000)

        # Use a stable accessible selector for the share button with one retry.
        if not self.click_button('Share', timeout_ms=10_000, retries=1):
            self.page.wait_for_timeout(300)
            self.click_button('Share', timeout_ms=5_000)

        self.page.wait_for_timeout(500)  # allow clipboard copy to complete
        return self.page.evaluate('navigator.clipboard.readText()')
