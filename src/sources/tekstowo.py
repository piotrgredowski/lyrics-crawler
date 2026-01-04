from ..crawler import LyricsSource
from playwright.async_api import Page


class TekstowoSource(LyricsSource):
    """Tekstowo.pl lyrics source."""

    async def search(self, page: Page, artist: str, title: str) -> str | None:
        """Search for lyrics on Tekstowo.pl."""
        # 1. Try direct URL first (faster)
        artist_slug = artist.lower().replace(" ", "_").replace("'", "_").replace(".", "").replace("&", "_")
        title_slug = title.lower().replace(" ", "_").replace("'", "_").replace(".", "").replace("&", "_")
        
        # Handle special case for "n'" -> "_"
        artist_slug = artist_slug.replace("n_", "n_") # naive, but let's try basic slugification first
        
        # Tekstowo slugs are a bit specific, e.g. "Guns N' Roses" -> "guns_n_roses"
        # Let's try basic normalization first
        
        direct_url = f"https://www.tekstowo.pl/piosenka,{artist_slug},{title_slug}.html"
        
        try:
            await page.goto(direct_url, timeout=10000)
            
            # Check if we got a 404
            title_element = await page.title()
            if "Nie ma takiego pliku" in title_element or "404" in title_element:
                raise Exception("Direct URL failed")

            return await self._extract_lyrics(page)
        except Exception:
            # 2. Fallback to search
            query = f"{artist} {title}".replace(" ", "+")
            search_url = f"https://www.tekstowo.pl/szukaj,{query}.html"
            
            try:
                await page.goto(search_url, timeout=15000)
                await self.with_delay(
                    page.wait_for_selector("div.content a.title", timeout=5000)
                )
                
                # Click first result
                # We need to be careful about the cookie banner blocking clicks
                # Try to accept cookies if banner is present
                try:
                    accept_btn = page.get_by_role("button", name="Zgadzam się")
                    if await accept_btn.is_visible():
                        await accept_btn.click()
                except Exception:
                    pass

                # Find result links (they usually have class 'title' inside content)
                # In snapshot: link "Nirvana - Smells Like Teen Spirit" points to /piosenka,...
                # Let's try to find the link by href starting with /piosenka,
                
                results = await page.query_selector_all("a[href^='/piosenka,']")
                if not results:
                    return None
                
                # Click the first one
                await results[0].click()
                await page.wait_for_load_state("networkidle", timeout=5000)
                
                return await self._extract_lyrics(page)
            except Exception:
                return None

    async def _extract_lyrics(self, page: Page) -> str | None:
        try:
            # Try to handle cookie banner
            try:
                accept_btn = page.get_by_role("button", name="Zgadzam się")
                if await accept_btn.is_visible():
                    await accept_btn.click()
            except Exception:
                pass

            # Wait for lyrics content
            # Strategy: Find "Tekst piosenki:" heading and get the lyrics container below it
            # The lyrics are usually in a div with class 'inner-text'
            
            try:
                # Try specific class first (common on Tekstowo)
                element = await page.query_selector("div.inner-text")
                if element:
                    return (await element.inner_text()).strip()
            except Exception:
                pass

            # Fallback: Look for header and next div
            # "Tekst piosenki:" is usually in h2
            # Lyrics are in the div immediately following the h2 section
            
            # Use a locator to find the section
            # We can use text locator
            header = page.get_by_text("Tekst piosenki:", exact=False)
            if await header.count() > 0:
                # Get the lyrics container. 
                # Structure is often: <h2>...</h2> <div class="inner-text">...</div>
                # But sometimes structure varies.
                # Let's try to get the .inner-text again, maybe I missed it.
                pass
            
            # Let's try to just return the inner-text if we find it
            element = await page.wait_for_selector(".inner-text", timeout=3000)
            if element:
                return (await element.inner_text()).strip()
                
            return None

        except Exception:
            return None
