"""Province records: enough of them to answer "who holds this province?".

The full province record layout is still unmapped. What is decoded here is the
one field that matters most for analysis -- the **owner** -- because without it
a battle report cannot tell a victory from a defeat. Inferred casualty counts
cannot: a turn file only shows what its owner can see, so losing a battle makes
the enemy look annihilated.

Records are located by their own signature: the province name is stored twice
in immediate succession (probably current name and base name, since renaming is
a game feature). Battle replays repeat that pattern, so replay spans are
excluded.

⚠️ **Enumeration is incomplete.** Measured against the score record, this finds
about 90% of owned provinces -- every nation comes up 1-2 short, none over.
Some province records evidently do not match the twice-repeated-name signature.
So treat a province that is *found* as reliable and a province that is
*missing* as unknown; never infer "not owned" from absence. `owner_of()`
returns None rather than guessing.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Owner id, relative to the end of the province's second name string.
#: 🟡 Probable: chosen because it is the only offset at which the per-nation
#: counts reproduce the score record's province column across both files of
#: two different games. Not yet confirmed against a fully mapped record.
OWNER_OFFSET = 34

#: Owner 0 means independent, or -- in a .trn -- a province the player has
#: never seen. The two are indistinguishable from a turn file alone.
INDEPENDENT = 0


@dataclass(frozen=True)
class Province:
    name: str
    owner: int
    offset: int  #: start of the record's first name string

    @property
    def is_independent_or_unseen(self) -> bool:
        return self.owner == INDEPENDENT


def find_provinces(save) -> list[Province]:
    """Every province record whose signature is recognisable, in file order.

    Takes a `SaveFile` rather than raw bytes because it needs both the string
    scan and the battle-replay spans to exclude.
    """
    data = save.data
    spans = [(b.offset, b.end_offset or len(data)) for b in save.battles]
    strings = save.strings(min_len=3, clean=False)

    out: list[Province] = []
    for (off_a, text_a), (off_b, text_b) in zip(strings, strings[1:]):
        if text_a != text_b or off_b != off_a + len(text_a) + 1:
            continue
        if any(lo <= off_a < hi for lo, hi in spans):
            continue  # a battle replay stores its province name twice too
        owner_at = off_b + len(text_b) + 1 + OWNER_OFFSET
        if owner_at >= len(data):
            continue
        out.append(Province(name=text_a, owner=data[owner_at], offset=off_a))
    return out


def owner_of(save, name: str) -> int | None:
    """Owner nation id of a named province, or None if the record was not found.

    None means "cannot tell", never "nobody" -- see the enumeration caveat.
    """
    for prov in find_provinces(save):
        if prov.name == name:
            return prov.owner
    return None
