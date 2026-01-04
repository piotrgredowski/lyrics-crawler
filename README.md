# Lyrics Crawler

A robust, asynchronous lyrics scraper that collects song lyrics from multiple sources with automatic fallback and load distribution.

**⚠️ Educational purposes only. Using this tool may violate the terms of service of lyrics websites.**

## Features

- 🕷️ **Multi-Source Support**: Scrapes from Genius, AZLyrics, and Tekstowo.pl.
- 🔄 **Smart Rotation**: Randomly shuffles sources per song to distribute load and avoid bans.
- 💾 **Resume Capability**: Skips already scraped songs if interrupted.
- ⚡ **Asynchronous**: Built with `asyncio` and `playwright` for performance.
- 🕵️ **Stealthy**: Uses headless browser with randomized user agents.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Option 1: Install as a tool (Recommended)

To install the tool globally:

```bash
uv tool install .
uv run playwright install chromium
```

### Option 2: Local development

To set up the environment locally:

```bash
uv sync
uv run playwright install chromium
```

## Usage

1. **Create a songs file** (`songs.txt`):
   ```text
   Nirvana - Smells Like Teen Spirit
   Queen - Bohemian Rhapsody
   Pink Floyd - Don't Stop Me Now
   ```

2. **Run the crawler:**

   If installed as a tool:
   ```bash
   lyrics-crawler songs.txt
   ```

   Or via uv run:
   ```bash
   uv run lyrics-crawler songs.txt
   ```

### Options

| Flag | Description |
|------|-------------|
| `-o`, `--output` | Output directory (default: `output/`) |
| `-d`, `--delay` | Base delay between requests in seconds (default: 3.0) |
| `-r`, `--resume` | Resume from previous progress |
| `--no-headless` | Run with visible browser (for debugging) |

## Output

Lyrics are saved as text files in the output directory, organized by artist:
```
output/
└── Nirvana/
    └── Smells Like Teen Spirit.txt
```
