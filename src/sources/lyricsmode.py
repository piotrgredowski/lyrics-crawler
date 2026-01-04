from ..crawler import LyricsSource
from playwright.async_api import Page


class LyricsModeSource(LyricsSource):
    """LyricsMode lyrics source."""

    async def search(self, page: Page, artist: str, title: str) -> str | None:
        """Search for lyrics on LyricsMode."""
        query = f"{artist} {title}".replace(" ", "_").lower()
        url = f"https://www.lyricsmode.com/lyrics/{query}.html"

        try:
            await page.goto(url, timeout=15000)
            await self.with_delay(
                page.wait_for_selector("div.lyrics", timeout=5000)
            )

            lyrics_element = await page.query_selector("div.lyrics")
            if not lyrics_element:
                return None

            lyrics = await lyrics_element.inner_text()
            return lyrics.strip()
        except Exception:
            return None
