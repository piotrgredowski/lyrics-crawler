from ..crawler import LyricsSource
from playwright.async_api import Page


class LyricFindSource(LyricsSource):
    """LyricFind lyrics source."""

    async def search(self, page: Page, artist: str, title: str) -> str | None:
        """Search for lyrics on LyricFind."""
        query = f"{artist} {title}".replace(" ", "%20")
        url = f"https://www.lyricfind.com/lyrics/{query}"

        try:
            await page.goto(url, timeout=15000)
            await self.with_delay(page.wait_for_selector("lyric-find-lrc", timeout=5000))

            lyrics_element = await page.query_selector("lyric-find-lrc")
            if not lyrics_element:
                return None

            lyrics = await lyrics_element.inner_text()
            return lyrics.strip()
        except Exception:
            return None
