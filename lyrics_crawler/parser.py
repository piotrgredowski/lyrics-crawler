from dataclasses import dataclass
from pathlib import Path


@dataclass
class Song:
    artist: str
    title: str
    album: str | None = None


def parse_input_file(file_path: str) -> list[Song]:
    """Parse songs.txt file.

    Supports two formats:
    1. Simple: "Artist - Title" per line
    2. Album-based:
       [Album: Album Name - Artist]
       Song Title 1
       Song Title 2
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    songs: list[Song] = []
    current_album: str | None = None
    current_artist: str | None = None

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Album header format: [Album: Album Name - Artist]
            if line.startswith("[Album:") and line.endswith("]"):
                content = line[7:-1]  # Remove "[Album:" and "]"
                if " - " in content:
                    current_album, current_artist = content.split(" - ", 1)
                    current_album = current_album.strip()
                    current_artist = current_artist.strip()
                continue

            # Simple format: "Artist - Title"
            if " - " in line:
                parts = line.split(" - ", 1)
                artist = parts[0].strip()
                title = parts[1].strip()
                songs.append(Song(artist=artist, title=title))
            # Song title only (within album section)
            elif current_artist:
                songs.append(Song(artist=current_artist, title=line, album=current_album))

    return songs
