from ..crawler import LyricsSource
from playwright.async_api import Page


class LyricsComSource(LyricsSource):
    """Lyrics.com lyrics source."""

    async def search(self, page: Page, artist: str, title: str) -> str | None:
        """Search for lyrics on Lyrics.com."""
        query = f"{artist} {title}".replace(" ", "+")
        url = f"https://www.lyrics.com/lyrics/{query}"

        try:
            await page.goto(url, timeout=15000)
            await self.with_delay(
                page.wait_for_selector("div.lyric__body", timeout=5000)
            )

            lyrics_element = await page.query_selector("div.lyric__body")
            if not lyrics_element:
                return None

            lyrics = await lyrics_element.inner_text()
            return lyrics.strip()
        except Exception:
            return None
