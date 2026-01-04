from ..crawler import LyricsSource
from playwright.async_api import Page


class GeniusSource(LyricsSource):
    """Scrape lyrics from Genius.com."""

    BASE_URL = "https://genius.com"

    async def search(self, page: Page, artist: str, title: str) -> str | None:
        query = f"{artist} {title}".replace(" ", "-").lower()
        url = f"{self.BASE_URL}/{query}-lyrics"

        try:
            await page.goto(url, timeout=30000)
            await page.wait_for_selector("[data-lyrics-container='true']", timeout=10000)

            # Extract lyrics from containers
            lyrics_parts = await page.eval_on_selector_all(
                "[data-lyrics-container='true']",
                "els => els.map(el => el.innerText).join('\\n')"
            )

            return lyrics_parts if lyrics_parts else None
        except Exception:
            return None
