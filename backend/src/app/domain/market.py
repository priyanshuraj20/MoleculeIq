"""
domain/market.py

Internal domain models for market intelligence data.

These are plain Python dataclasses — they have no knowledge of Supabase,
HTTP, or any external system. The repository layer maps raw DB rows into
these types before handing them up to the agent layer.

Why dataclasses?
  Lightweight, readable, no extra dependencies. We get __repr__ and
  equality checks for free which helps with testing.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MarketDataPoint:
    """
    One row from the iqvia_sales table.
    Represents market size for a molecule in a specific year and region.
    """
    molecule_name:      str
    year:               int
    region:             str
    therapeutic_area:   str
    market_size_usd_mn: float          # USD millions
    cagr_percent:       Optional[float] # 5-year CAGR, can be missing
    competitor_count:   int
    data_source:        str


@dataclass
class MarketInsightsDomain:
    """
    Aggregated market intelligence for one molecule.
    This is what the Market Agent writes into AgentState.

    Holds a list of MarketDataPoint rows plus computed convenience
    properties so agents don't re-implement the same logic.
    """
    molecule_name: str
    data_points:   list[MarketDataPoint] = field(default_factory=list)
    source:        str   = "Supabase / IQVIA MIDAS (mock)"
    confidence:    Optional[float] = None  # Scientifically computed during Hybrid Scoring (Phase 5)

    @property
    def global_market_size_usd_mn(self) -> Optional[float]:
        """Most recent global market size figure, or None if not found."""
        global_rows = [d for d in self.data_points if d.region == "Global"]
        if not global_rows:
            return None
        # Take the most recent year
        return max(global_rows, key=lambda x: x.year).market_size_usd_mn

    @property
    def latest_cagr(self) -> Optional[float]:
        """Most recent CAGR from the global data row."""
        global_rows = [d for d in self.data_points if d.region == "Global"]
        if not global_rows:
            return None
        return max(global_rows, key=lambda x: x.year).cagr_percent

    @property
    def is_empty(self) -> bool:
        """True when no data was found for this molecule."""
        return len(self.data_points) == 0
