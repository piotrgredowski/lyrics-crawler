import asyncio
import random
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from playwright.async_api import async_playwright, Browser, Page

logger = logging.getLogger(__name__)


@dataclass
class Song:
    artist: str
    title: str


@dataclass
class ScrapingResult:
    lyrics: str | None
    source: str
    success: bool


class LyricsSource(ABC):
    """Base class for lyrics sources."""

    def __init__(self, delay: tuple[float, float] = (2.0, 5.0)):
        self.delay_range = delay

    @abstractmethod
    async def search(self, page: Page, artist: str, title: str) -> str | None:
        """Search for lyrics and return them if found."""
        pass

    async def with_delay(self, coro):
        """Execute coroutine with random delay before."""
        await asyncio.sleep(random.uniform(*self.delay_range))
        return await coro


class LyricsCrawler:
    """Main crawler using Playwright headless browser."""

    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(
        self,
        sources: list[LyricsSource],
        output_dir: str = "output",
        delay: tuple[float, float] = (2.0, 5.0),
        headless: bool = True,
    ):
        self.sources = sources
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.headless = headless
        self.browser: Browser | None = None
        self.progress_file = Path("progress.json")

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        return self

    async def __aexit__(self, *args):
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()

    async def _create_context(self):
        """Create browser context with random user agent."""
        return await self.browser.new_context(
            user_agent=random.choice(self.USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
        )

    def _load_progress(self) -> set[str]:
        """Load completed songs from progress file."""
        if not self.progress_file.exists():
            return set()
        import json
        with open(self.progress_file, "r") as f:
            data = json.load(f)
            return set(data.get("completed", []))

    def _save_progress(self, completed: set[str]):
        """Save progress to file."""
        import json
        with open(self.progress_file, "w") as f:
            json.dump({"completed": list(completed)}, f, indent=2)

    def _get_song_key(self, artist: str, title: str) -> str:
        """Get unique key for a song."""
        return f"{artist.lower()}|{title.lower()}"

    async def scrape_song(self, artist: str, title: str) -> ScrapingResult:
        """Try to scrape lyrics from multiple sources with fallback."""
        context = await self._create_context()
        page = await context.new_page()

        # Shuffle sources for each song to distribute load
        shuffled_sources = self.sources.copy()
        random.shuffle(shuffled_sources)

        try:
            for source in shuffled_sources:
                logger.info(f"Trying {source.__class__.__name__}")
                try:
                    result = await source.search(page, artist, title)
                    if result:
                        return ScrapingResult(
                            lyrics=self._clean_lyrics(result),
                            source=source.__class__.__name__,
                            success=True,
                        )
                except Exception as e:
                    logger.error(f"{source.__class__.__name__} failed: {e}")
                    continue

            return ScrapingResult(lyrics=None, source="None", success=False)
        finally:
            await context.close()

    def _clean_lyrics(self, lyrics: str) -> str:
        """Remove common artifacts from scraped lyrics."""
        lines = []
        for line in lyrics.split("\n"):
            line = line.strip()
            # Skip common footer/header text
            if any(x in line.lower() for x in [
                "embed", "copy", "you might also like", "see also",
                "lyrics provided by", "submit lyrics", "corrections",
            ]):
                continue
            lines.append(line)
        return "\n".join(lines).strip()

    def _save_lyrics(self, artist: str, title: str, lyrics: str):
        """Save lyrics to file."""
        # Sanitize filenames
        safe_artist = "".join(c for c in artist if c.isalnum() or c in (" ", "-", "_")).strip()
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()

        artist_dir = self.output_dir / safe_artist
        artist_dir.mkdir(parents=True, exist_ok=True)

        file_path = artist_dir / f"{safe_title}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"{artist} - {title}\n\n{lyrics}")

    async def run(self, songs: list[Song], resume: bool = False) -> dict:
        """Run scraping for all songs."""
        completed = self._load_progress() if resume else set()
        results = {"success": 0, "failed": 0, "skipped": 0, "failed_songs": []}

        for i, song in enumerate(songs, 1):
            key = self._get_song_key(song.artist, song.title)
            if key in completed:
                logger.info(f"[{i}/{len(songs)}] SKIP: {song.artist} - {song.title}")
                results["skipped"] += 1
                continue

            logger.info(f"[{i}/{len(songs)}] Scraping: {song.artist} - {song.title}")
            result = await self.scrape_song(song.artist, song.title)

            if result.success:
                self._save_lyrics(song.artist, song.title, result.lyrics)
                completed.add(key)
                self._save_progress(completed)
                logger.info(f"Found via {result.source}")
                results["success"] += 1
            else:
                logger.warning(f"Not found on any source")
                results["failed"] += 1
                results["failed_songs"].append(f"{song.artist} - {song.title}")

            # Rate limiting between songs
            if i < len(songs):
                await asyncio.sleep(random.uniform(*self.delay))

        return results
