"""Timecode parsing and formatting.

Source timestamps appear in three places — config (``"4:10"``), frame filenames
(``t14m02s``) and generated Markdown (``14:02``) — so the conversions live in one
module rather than being re-derived per caller. Milliseconds are the internal
unit everywhere; a float number of seconds cannot be compared for equality
across a re-run and frame ids must be stable (DEC-013).
"""

from __future__ import annotations

import re

_CLOCK = re.compile(r"^(?:(?P<h>\d+):)?(?P<m>\d{1,2}):(?P<s>\d{1,2})(?:\.(?P<frac>\d{1,3}))?$")
_BARE_SECONDS = re.compile(r"^(?P<s>\d+)(?:\.(?P<frac>\d{1,3}))?$")


class TimecodeError(ValueError):
    """A timecode in config could not be parsed.

    Raised rather than guessed: a silently mis-parsed ``skip_ranges`` entry drops
    footage from the catalogue without telling anyone.
    """


def parse_timecode(value: str | int | float) -> int:
    """Parse ``"14:02"``, ``"1:14:02"``, ``"14:02.500"`` or ``902`` into milliseconds."""
    if isinstance(value, bool):  # bool is an int subclass; never a timecode
        raise TimecodeError(f"not a timecode: {value!r}")
    if isinstance(value, int | float):
        if value < 0:
            raise TimecodeError(f"negative timecode: {value!r}")
        return round(float(value) * 1000)

    text = value.strip()
    match = _CLOCK.match(text) or _BARE_SECONDS.match(text)
    if match is None:
        raise TimecodeError(
            f"cannot parse timecode {value!r} — expected MM:SS, H:MM:SS or a number of seconds"
        )
    parts = match.groupdict()
    hours = int(parts.get("h") or 0)
    minutes = int(parts.get("m") or 0)
    seconds = int(parts["s"])
    frac = parts.get("frac") or "0"
    millis = int(frac.ljust(3, "0"))
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + millis


def format_timecode(t_ms: int) -> str:
    """Format milliseconds as ``MM:SS`` (or ``H:MM:SS`` past an hour), for humans."""
    total_seconds, _ = divmod(max(t_ms, 0), 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def format_stamp(t_ms: int) -> str:
    """Format milliseconds as the filename-safe ``14m02s`` used in frame names.

    Frame filenames carry the source timestamp so that re-extracting a screen at
    full resolution never depends on a side index that can drift out of date
    (DEC-004).
    """
    total_seconds, _ = divmod(max(t_ms, 0), 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{seconds:02d}s"
    return f"{minutes:02d}m{seconds:02d}s"


def parse_range(pair: tuple[str | int | float, str | int | float]) -> tuple[int, int]:
    """Parse a ``[from, to]`` config pair into an inclusive-exclusive ms range."""
    start = parse_timecode(pair[0])
    end = parse_timecode(pair[1])
    if end <= start:
        raise TimecodeError(f"range ends before it starts: {pair[0]!r} → {pair[1]!r}")
    return start, end
