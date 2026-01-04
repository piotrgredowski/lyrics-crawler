from ..crawler import LyricsSource
from playwright.async_api import Page


class AZLyricsSource(LyricsSource):
    """Scrape lyrics from AZLyrics.com."""

    BASE_URL = "https://www.azlyrics.com"

    async def search(self, page: Page, artist: str, title: str) -> str | None:
        # AZLyrics URL format: /lyrics/artist/title.html
        artist_slug = artist.lower().replace(" ", "").replace(".", "")
        title_slug = title.lower().replace(" ", "").replace(".", "")
        url = f"{self.BASE_URL}/lyrics/{artist_slug}/{title_slug}.html"

        try:
            await page.goto(url, timeout=30000)
            await page.wait_for_selector(".main-page", timeout=10000)

            # AZLyrics has lyrics in div with class not-used, inside main-page
            lyrics = await page.locator(".main-page .not-used").inner_text()

            return lyrics if lyrics else None
        except Exception:
            return None
