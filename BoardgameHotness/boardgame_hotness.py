#!/usr/bin/env python
# encoding=utf8
"""Boardgame Geek Hot Games List."""

class Boardgame:
    """Boardgame Class."""

    def __init__ (self, game_id, title, rank, year_published):
        """Create Variables."""
        self.game_id = game_id
        self.title  = title
        self.rank = rank
        self.year_published = year_published
