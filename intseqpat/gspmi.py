from __future__ import annotations

from collections import Counter
from math import inf
from typing import Callable, List, NamedTuple, Set, Tuple, Union

import pandas as pd


class Item(NamedTuple):
    """Item of input interval seqences.

    Attributes:
        interval: Interval from first item (without itemize transformation).
        elements: Elements of the item.
    """

    interval: int
    elements: Set[str]

    def exclude(self, element: str) -> Item:
        """Exclude previous elements according to the alphabet order."""
        elements = sorted(self.elements)
        elements = set(elements[elements.index(element) + 1:])
        return Item(self.interval, elements)

    def minus(self, interval: int) -> Item:
        """Minus interal of this item."""
        return Item(self.interval - interval, self.elements)


class Pair(NamedTuple):
    """Pair including interval and element of output pattern.

    Attributes:
        interval: Interval from previous pair (after itemize transformation).
        element: Element of the pair.
    """

    interval: int
    element: str


class Pattern(NamedTuple):
    """Interval sequential pattern.

    Args:
        sequence: The interval sequence.
        support: Number of sequences the pattern exists.
        count: Number of places the pattern exists.
        whole_interval: the interval from the first to the last pair.
    """

    sequence: List[Pair]
    support: int
    count: int
    whole_interval: int


def generate_postfixes(sequence: List[Item],
                       projector: str) -> List[List[Item]]:
    """Find projector in each place of sequence and generate postfix.

    Args:
        projector (str): The element to match.
    """
    postfixes = []
    for i, item in enumerate(sequence):
        if projector in item.elements:
            postfix = [it.minus(item.interval) for it in sequence[i + 1:]]

            first = item.exclude(projector)
            if first.elements:
                postfix.insert(0, first.minus(item.interval))

            if postfix:
                postfixes.append(postfix)

    return postfixes


def postfix(sequence: List[Item], projector: Pair,
            itemize: Callable[[int], int]) -> List[Item]:
    """Generate postfix according to sequence and projector.

    Args:
        projector (Pair): The pair to match.
    """
    for i, item in enumerate(sequence):
        if (projector.element in item.elements
                and itemize(item.interval) == projector.interval):
            postfix = [it.minus(item.interval) for it in sequence[i + 1:]]

            first = item.exclude(projector.element)
            if first.elements:
                postfix.insert(0, first.minus(item.interval))

            return postfix
    else:
        return []


def project(
    sequences: pd.Series,
    itemize: Callable[[int], int],
    prefix: List[Pair],
    min_support: int,
    min_interval: int,
    max_interval: int,
    min_whole_interval: int,
    max_whole_interval: int,
) -> List[Pattern]:
    """Apply algorithm on sequences after postfixes generating.
    
    Args:
        sequences: Pandas Series with two level index: first is the orgin SN, 
            second level represent generated postfixes in each place of the seqeuce.
        prefix: List of Previous projectors.
    """
    pass


def gspmi(
    sequences: Union[List[List[Item]], List[Tuple[int, Set[str]]]],
    itemize: Callable[[int], int],
    min_support: Union[float, int],
    min_interval: int = 0,
    max_interval: int = inf,
    min_whole_interval: int = 0,
    max_whole_interval: int = inf,
) -> List[Pattern]:
    """Apply algorithm on sequences to find interval sequential patterns.

    For four types of constrains (min/max interval and min/max whole interval),
    the unit is same as input sequences.

    Args:
        sequences: Sequences to mine, transform if in Tuple type.
        itemize: Itemize function to merge a interval to same item.
        min_support: Minimal support to mine pattern.
            If value is in float range from zero to one,
            transform to number according to the size of sequences.
        min_interval: Minimal interval between each pair of pattern.
        max_interval: Maximum interval between each pair of pattern.
        min_whole_interval: Minimal interval from the first to the last pair.
        max_whole_interval: Maximum interval from the first to the last pair.

    Returns:
        Pandas DataFrame with columns:
        1. sequence: The interval sequential pattern.
        2. support: Number of sequences the pattern exists.
        3. count: Number of places the pattern exists.
        3. whole_interval: the interval from the first to the last pair.
    """
    pass
