from ..crawler import LyricsSource
from playwright.async_api import Page


class MusixmatchSource(LyricsSource):
    """Musixmatch lyrics source."""

    async def search(self, page: Page, artist: str, title: str) -> str | None:
        """Search for lyrics on Musixmatch."""
        query = f"{artist} {title}".replace(" ", "-")
        url = f"https://www.musixmatch.com/lyrics/{query}"

        try:
            await page.goto(url, timeout=15000)
            await self.with_delay(
                page.wait_for_selector("p.mxm-lyrics__content", timeout=5000)
            )

            # Get all lyric paragraphs
            lyrics_elements = await page.query_selector_all("p.mxm-lyrics__content")
            if not lyrics_elements:
                return None

            lyrics_lines = []
            for element in lyrics_elements:
                text = await element.inner_text()
                lyrics_lines.append(text.strip())

            return "\n".join(lyrics_lines).strip()
        except Exception:
            return None
