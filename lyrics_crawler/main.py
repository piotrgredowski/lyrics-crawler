import asyncio
import argparse
import random
import logging
from pathlib import Path

from lyrics_crawler.crawler import LyricsCrawler
from lyrics_crawler.parser import parse_input_file
from lyrics_crawler.sources import (
    GeniusSource,
    AZLyricsSource,
    TekstowoSource,
)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    parser = argparse.ArgumentParser(
        description="Scrape song lyrics using headless browser"
    )
    parser.add_argument(
        "input_file",
        help="Path to txt file with songs (format: 'Artist - Title' per line)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="output",
        help="Output directory for lyrics (default: output/)",
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=3.0,
        help="Base delay between requests in seconds (default: 3.0)",
    )
    parser.add_argument(
        "--resume",
        "-r",
        action="store_true",
        help="Resume from previous progress (skips already scraped songs)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run headless (default: True)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Run with visible browser (for debugging)",
    )

    args = parser.parse_args()

    # Parse input file
    print(f"Parsing songs from {args.input_file}...")
    songs = parse_input_file(args.input_file)
    print(f"Found {len(songs)} songs to scrape")

    # Setup all available sources
    all_sources = [
        GeniusSource(delay=(args.delay, args.delay + 2)),
        AZLyricsSource(delay=(args.delay, args.delay + 2)),
        TekstowoSource(delay=(args.delay, args.delay + 2)),
    ]

    # Shuffle sources to distribute load across different sites
    random.shuffle(all_sources)

    print(f"Using {len(all_sources)} lyrics sources (shuffled order)")

    # Run crawler
    async def run():
        async with LyricsCrawler(
            sources=all_sources,
            output_dir=args.output,
            delay=(args.delay, args.delay + 2),
            headless=args.headless,
        ) as crawler:
            results = await crawler.run(songs, resume=args.resume)

            print("\n" + "=" * 50)
            print("Scraping complete!")
            print(f"  Success: {results['success']}")
            print(f"  Failed:  {results['failed']}")
            print(f"  Skipped: {results['skipped']}")
            
            if results["failed_songs"]:
                print("\nFailed songs:")
                for song in results["failed_songs"]:
                    print(f"  - {song}")
            
            print(f"  Output:  {Path(args.output).absolute()}")
            print("=" * 50)

    asyncio.run(run())


if __name__ == "__main__":
    main()
