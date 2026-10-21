"""Canonical Mumbai Indians dynasty data — the single source of truth.

Every fact here is DERIVED FROM the Cricsheet ball-by-ball ledger
(data/cricsheet/ipl_json/), not from memory. Regenerate/verify with
tools/derive.py. Finals were filtered on info.event.stage == 'Final'
exactly (the naive 'Final' substring match also catches 'Semi-Final').

Units: margin_runs and margin_wickets are mutually exclusive; exactly one
is set per final. Years are the IPL *season label* (2020 final was played
2020-11-10 due to the COVID-shifted season; Cricsheet labels it '2020/21').
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Final:
    year: int           # season label
    date: str           # ISO date the final was played
    opponent: str
    margin_runs: int | None
    margin_wickets: int | None
    player_of_match: str
    note: str           # one-line narrative hook

    @property
    def margin_text(self) -> str:
        if self.margin_runs is not None:
            return f"{self.margin_runs} run{'s' if self.margin_runs != 1 else ''}"
        return f"{self.margin_wickets} wickets"


# The dynasty: 5 IPL titles, all under captain Rohit Sharma.
TITLES: tuple[Final, ...] = (
    Final(2013, "2013-05-26", "Chennai Super Kings", 23, None, "Kieron Pollard",
          "The first crown — Pollard's blitz buries CSK."),
    Final(2015, "2015-05-24", "Chennai Super Kings", 41, None, "Rohit Sharma",
          "The captain himself takes MVP."),
    Final(2017, "2017-05-21", "Rising Pune Supergiant", 1, None, "Krunal Pandya",
          "Won by 1 run — the closest final in IPL history, until..."),
    Final(2019, "2019-05-12", "Chennai Super Kings", 1, None, "Jasprit Bumrah",
          "...they did it AGAIN. 1 run over CSK. Bumrah ice-cold at the death."),
    Final(2020, "2020-11-10", "Delhi Capitals", None, 5, "Trent Boult",
          "Total dominance — the most complete title run of them all."),
)

# Headline numbers (derived; see tools/derive.py for the queries).
CAPTAIN = "Rohit Sharma"
TITLE_COUNT = len(TITLES)
FINALS_VS_CSK = sum(1 for f in TITLES if f.opponent == "Chennai Super Kings")
ONE_RUN_FINALS = tuple(f.year for f in TITLES if f.margin_runs == 1)

# Narrative-only facts NOT in the Cricsheet ledger — web-verified, cite on use.
EXTERNAL_FACTS = {
    "most_titles": "Tied for most IPL titles in history (5).",
    "owner": "Owned by Reliance Industries (Indiawin Sports).",
    "home": "Wankhede Stadium, Mumbai.",
}


def headline_stats() -> dict[str, str]:
    """Big on-screen numbers for the stat scenes."""
    return {
        "TITLES": str(TITLE_COUNT),
        "FINALS WON vs CSK": str(FINALS_VS_CSK),
        "ONE-RUN FINALS": str(len(ONE_RUN_FINALS)),
        "TITLES AS CAPTAIN (ROHIT)": str(TITLE_COUNT),
    }


if __name__ == "__main__":
    print(f"{CAPTAIN} — {TITLE_COUNT} titles, {FINALS_VS_CSK} finals beating CSK, "
          f"{len(ONE_RUN_FINALS)} one-run finals {ONE_RUN_FINALS}")
    for f in TITLES:
        print(f"  {f.year}  beat {f.opponent:<24} by {f.margin_text:<10} POM {f.player_of_match}")
