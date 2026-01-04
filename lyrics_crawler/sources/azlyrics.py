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

            # Find div containing the specific license comment
            # This is the most reliable way to find the lyrics container on AZLyrics
            xpath = '//div[comment()[contains(., "Usage of azlyrics.com content")]]'
            lyrics_element = page.locator(f"xpath={xpath}")
            
            if await lyrics_element.count() > 0:
                lyrics = await lyrics_element.first.inner_text()
                return lyrics.strip()
            
            return None
        except Exception:
            return None
