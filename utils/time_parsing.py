from __future__ import annotations

import re
import urllib.parse
from typing import List, TypedDict, Optional

__all__ = ["parse_line", "parse_text"]


class Parsed(TypedDict):
    url: str
    start: int
    end: int | None          # None ⇒ until end-of-video
    length: int | None       # None ⇔ unknown / inf
    start_hms: str
    end_hms: str | None      # None ⇔ inf
    section: str             # *HH:MM:SS-HH:MM:SS or *HH:MM:SS-inf


# ───────────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────────

_TIME_RE = re.compile(
    r"^(?:(?P<hours>\d+)h)?"
    r"(?:(?P<minutes>\d+)m)?"
    r"(?:(?P<seconds>\d+)s)?$"
)


def _parse_time(value: str) -> int:
    """Accept '1h2m3s', '90s', or plain seconds like '75'."""
    if value.isdigit():
        return int(value)

    m = _TIME_RE.fullmatch(value)
    if not m:
        raise ValueError(f"Invalid time specification: {value!r}")
    h = int(m.group("hours") or 0)
    m_ = int(m.group("minutes") or 0)
    s = int(m.group("seconds") or 0)
    return h * 3600 + m_ * 60 + s


def _sec_to_hhmmss(total: int) -> str:
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _timestamp_from_url(url: str) -> Optional[int]:
    """Return the seconds in ?t=… / #t=… / …start=…, or None."""
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    fr = urllib.parse.parse_qs(p.fragment)
    vals = qs.get("t", []) + qs.get("start", []) + fr.get("t", []) + fr.get("start", [])
    if not vals:
        return None
    try:
        return _parse_time(vals[0])
    except ValueError:
        return None


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────

def parse_line(line: str):
    """
    Parse *line* and return a ``Parsed`` mapping.

    New defaults
    ------------
    • ``URL``                    → whole video (*-inf*)
    • ``URL?…t=323``             → from 323 s to end (*-inf*)
    Everything else follows the old rules.
    """
    tokens = line.split()
    if not tokens:
        raise ValueError("Empty input line")

    url = tokens[0]
    start = _timestamp_from_url(url)
    end: Optional[int] = None
    length: Optional[int] = None
    explicit_e_end = False

    it = iter(tokens[1:])
    for t in it:
        if t in ("-s", "--start"):
            start = _parse_time(next(it))
        elif t in ("-e", "--end"):
            val = next(it)
            if val.lower() == "end":
                explicit_e_end = True
                end = None
            else:
                end = _parse_time(val)
        elif t in ("-l", "-t", "--length"):
            length = _parse_time(next(it))

    if start is None:
        start = 0

    # Decide what to do when neither end nor length is set
    if end is None and length is None and not explicit_e_end:
        if len(tokens) == 1:          # only URL → go to EOF
            pass                      # keep both None
        else:                         # user gave their own -s
            length = 30               # 30-second default
            end = start + length

    # Resolve end/length relationship
    if end is None and length is not None:
        end = start + length
    if length is None and end is not None:
        length = end - start

    start_hms = _sec_to_hhmmss(start)
    if end is None:
        end_hms = None
        section = f"*{start_hms}-inf"
    else:
        end_hms = _sec_to_hhmmss(end)
        section = f"*{start_hms}-{end_hms}"

    return {
        "url": url,
        "start": start,
        "end": end,
        "length": length,
        "start_hms": start_hms,
        "end_hms": end_hms,
        "section": section,
    }


def parse_text(text: str):
    """Parse every non-blank line into ``Parsed`` mappings."""
    return [parse_line(l) for l in text.splitlines() if l.strip()]


# ───────────────────────────────────────────────────────────────────────────────
# Demo
# ───────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = """
    https://youtu.be/r5WSDc2zHU0?t=323
    https://youtu.be/r5WSDc2zHU0
    https://example.com/video.mp4 -s 1m10s
    https://example.com/video.mp4 -s 1m -e end
    """
    import pprint, textwrap
    pprint.pp(parse_text(textwrap.dedent(sample)))
