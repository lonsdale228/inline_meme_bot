from __future__ import annotations

import re
from typing import List, Dict, TypedDict

__all__ = [
    "parse_line",
    "parse_text",
]


class Parsed(TypedDict):
    url: str
    start: int  # seconds
    end: int  # seconds
    length: int  # seconds
    start_hms: str  # HH:MM:SS
    end_hms: str  # HH:MM:SS
    section: str  # *HH:MM:SS-HH:MM:SS


# ────────────────────────────────────────────────────────────────────────────────
# Parsing helpers
# ────────────────────────────────────────────────────────────────────────────────

_TIME_RE = re.compile(
    r"^(?:(?P<hours>\d+)h)?"  # hours optional
    r"(?:(?P<minutes>\d+)m)?"  # minutes optional
    r"(?:(?P<seconds>\d+)s)?$"  # seconds optional
)


def _parse_time(value: str) -> int:
    """Convert a compact time spec like ``"1h2m3s"`` into seconds."""
    m = _TIME_RE.fullmatch(value)
    if not m:
        raise ValueError(f"Invalid time specification: {value!r}")
    h = int(m.group("hours") or 0)
    m_ = int(m.group("minutes") or 0)
    s = int(m.group("seconds") or 0)
    return h * 3600 + m_ * 60 + s


def _sec_to_hhmmss(total: int) -> str:
    """Return *total* seconds as ``HH:MM:SS`` with leading zeros."""
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def parse_line(line: str) -> Parsed:
    """Parse a single *line* and return a rich :class:`Parsed` mapping."""
    tokens = line.split()
    if not tokens:
        raise ValueError("Empty input line")

    url = tokens[0]
    start = end = length = None  # type: ignore[assignment]

    it = iter(tokens[1:])
    for t in it:
        if t in ("-s", "--start"):
            start = _parse_time(next(it))
        elif t in ("-e", "--end"):
            end = _parse_time(next(it))
        elif t in ("-l", "-t", "--length"):
            length = _parse_time(next(it))

    if start is None:
        raise ValueError("Missing required -s/--start parameter")
    if end is None and length is None:
        raise ValueError("Either -e/--end or -l/-t/--length is required")
    if end is None:
        end = start + length  # type: ignore[operator]

    start_hms = _sec_to_hhmmss(start)
    end_hms = _sec_to_hhmmss(end)
    section = f"*{start_hms}-{end_hms}"

    return {
        "url": url,
        "start": start,
        "end": end,
        "length": end - start,  # type: ignore[operator]
        "start_hms": start_hms,
        "end_hms": end_hms,
        "section": section,
    }


def parse_text(text: str) -> List[Parsed]:
    """Parse every non‑blank line of *text* into :class:`Parsed` mappings."""
    return [parse_line(l) for l in text.splitlines() if l.strip()]


if __name__ == "__main__":  # simple demo when run directly
    sample = """
    https:/sdadsa -s 10h10m -e 10h20m30s
    https:/sdadsa -s 10h10m10s -e 10h20m30s
    https:/sdadsa -s 10h10m10s -l 1m30s
    https:/sdadsa -s 10s -e 30s
    https:/sdadsa -s 10m10s -e 10m30s
    """
    import pprint, textwrap
    pprint.pp(parse_text(textwrap.dedent(sample)))
