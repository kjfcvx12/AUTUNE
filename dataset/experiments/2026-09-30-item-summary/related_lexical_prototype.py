"""Which other lines of a meeting are about the same thing as one line.

An action item's sentence is often a pointer -- "그건 다음 빌드에 넣을게요" -- and
what it points at was said earlier, sometimes many turns earlier and not next to
it. The lines just before it are the resolver's window; this finds the ones that
are *about the same thing* wherever they sit in the meeting, so the summary of
an item can draw on them and the screen can show them beneath it.

**Word overlap, weighted by rarity; no model.** Each line becomes the two-letter
pieces of its words, weighted by how few lines of the meeting contain them
(a piece every line has -- the ending of "-습니다" -- counts for nothing), and
two lines are as similar as the angle between those weightings. Deterministic, so
what the summary was written from is what the screen shows later, and nothing
leaves the process. It reads surface wording, not meaning: "버그" and "오류" are
strangers to it. An embedding model would close that gap and is a setting away
(``embedder_impl``); this is the floor that needs nothing.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Collection, Sequence

_WORD = re.compile(r"[가-힣A-Za-z0-9]+")

MIN_LENGTH = 8
"""A line shorter than this (after stripping) is an answer or a filler -- "네 좋아요",
"그렇게 하죠" -- and says too little to be about anything."""

MIN_SCORE = 0.25
"""Below this the overlap is a shared common word, not a shared subject."""

MAX_RELATED = 3


def _pieces(text: str) -> Counter[str]:
    """Two-letter pieces of the line's words, leaving out its last word.

    The last word of a Korean sentence is the predicate -- "드릴게요", "넣어 보려고요"
    -- and two lines that both end in a promise are not about the same thing. What
    a line is about sits in the words before it. A one-word line keeps its word.
    """
    pieces: Counter[str] = Counter()
    words = _WORD.findall(text.lower())
    for word in words[:-1] if len(words) > 1 else words:
        if len(word) < 2:
            continue
        for i in range(len(word) - 1):
            pieces[word[i : i + 2]] += 1
    return pieces


def related_ids(
    target_id: str,
    lines: Sequence[tuple[str, str]],
    *,
    exclude: Collection[str] = (),
    limit: int = MAX_RELATED,
    min_score: float = MIN_SCORE,
) -> list[str]:
    """The ids of the lines most like ``target_id``'s, in spoken order.

    ``lines`` is the meeting in spoken order as ``(id, text)``, blank lines and
    non-consenting speakers' lines already removed by the caller -- the same
    filtered sequence every other read of the transcript uses. ``exclude`` are
    lines to leave out whatever their score (the target itself is always left
    out): the ones the reader is already being shown.
    """
    texts = dict(lines)
    target = texts.get(target_id)
    if target is None:
        return []
    pieces = {line_id: _pieces(text) for line_id, text in lines}
    frequency: Counter[str] = Counter()
    for counted in pieces.values():
        frequency.update(counted.keys())
    total = len(pieces)

    def weigh(counted: Counter[str]) -> dict[str, float]:
        return {p: n * math.log(total / frequency[p]) for p, n in counted.items() if frequency[p]}

    wanted = weigh(pieces[target_id])
    norm = math.sqrt(sum(v * v for v in wanted.values()))
    if not norm:
        return []

    skip = {target_id, *exclude}
    scored: list[tuple[float, int, str]] = []
    for position, (line_id, text) in enumerate(lines):
        if line_id in skip or len(text.strip()) < MIN_LENGTH:
            continue
        other = weigh(pieces[line_id])
        other_norm = math.sqrt(sum(v * v for v in other.values()))
        if not other_norm:
            continue
        dot = sum(v * other.get(p, 0.0) for p, v in wanted.items())
        score = dot / (norm * other_norm)
        if score >= min_score:
            scored.append((score, position, line_id))
    best = sorted(scored, key=lambda s: (-s[0], s[1]))[:limit]
    return [line_id for _, _, line_id in sorted(best, key=lambda s: s[1])]
