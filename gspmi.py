from cmath import inf
from collections import Counter
from itertools import tee
from math import ceil, isinf
from typing import Callable, Generator, Hashable, List, NamedTuple, Set, Union


class Item(NamedTuple):
    """Item of sequence.
    
    interval: interval from zero without itemize transformation
    """

    interval: int
    elements: Set[Hashable]


class Pair(NamedTuple):
    """Pair of sequence.

    interval: interval from previous pair after itemize transformation
    """

    interval: int
    element: Hashable


class Pattern(NamedTuple):
    """Mined pattern

    Attributes:
        support: count of pattern occcurence
        whole_interval: interval from begining to the end 
            based on itemized intervals
    """

    sequence: List[Pair]
    support: int
    whole_interval: int


def generate_postfixes(sequence: List[Item],
                       projector: Pair,
                       itemize: Callable[[int], int],
                       level1: bool = False) -> Generator[Item, None, None]:
    """Yield postfixs according to projector.

    The function will yield all element-matched postfix from begining for 
    level1 == True; otherwise only one exactly interval-element matched postfix.
    If no matched, return nothing
    """

    def exclude(elements):
        elements = sorted(elements)
        return set(elements[elements.index(projector.element) + 1:])

    for i, (interval, elements) in enumerate(sequence):
        if (projector.element in elements
                and (level1 or itemize(interval) == projector.interval)):
            head = exclude(elements)
            postfix = [Item(0, head)] if head else []

            postfix.extend(Item(i - interval, e) for i, e in sequence[i + 1:])
            yield postfix

            if not level1:
                break


def project_level1(sequences: List[List[Item]], projector: Pair,
                   itemize: Callable[[int], int]) -> List[List[List[Item]]]:
    """Project from initial sequence database.

    Each sequence in database will be project to a list of postfix.
    """
    projected_db = []
    for sequence in sequences:
        if (postfixes := list(
                generate_postfixes(sequence, projector, itemize,
                                   level1=True))):
            projected_db.append(postfixes)

    return projected_db


def project(projected_db: List[List[List[Item]]], projector: Pair,
            itemize: Callable[[int], int]) -> List[List[List[Item]]]:
    """Project projected database to next level."""
    child_projected_db = []
    for sequences in projected_db:
        projected_sequences = []

        for sequence in sequences:
            postfix = next(generate_postfixes(sequence, projector, itemize),
                           None)
            if postfix:
                projected_sequences.append(postfix)

        if projected_sequences:
            child_projected_db.append(projected_sequences)

    return child_projected_db


def mine_subpatterns(projected_db: List[List[List[Item]]], prefix: List[Pair],
                     itemize: Callable[[int], int], min_support: int,
                     min_interval: int, max_interval: Union[int, float],
                     min_whole_interval: int,
                     max_whole_interval: Union[int, float]) -> List[Pattern]:
    """Recursivly mine sub patterns.

    Args:
        prefix: list of projectors generate during projections
        min_support (int): minimum count of patterns occurrence
    """
    counter = Counter()
    for sequences in projected_db:
        pairs = set()

        for sequence in sequences:
            previous = 0
            for interval, elements in sequence:
                if min_interval <= interval - previous <= max_interval:
                    pairs.update(Pair(itemize(interval), e) for e in elements)

                previous = interval

        counter.update(pairs)

    patterns = []
    for pair, support in counter.items():
        whole_interval = sum(i for i, p in prefix) + pair.interval
        if (support >= min_support
                and (isinf(max_whole_interval)
                     or whole_interval <= itemize(max_whole_interval))):
            child_projected_db = project(projected_db, prefix[-1], itemize)

            patterns.extend(
                mine_subpatterns(child_projected_db, prefix, itemize,
                                 min_support, min_interval, max_interval,
                                 min_whole_interval, max_whole_interval))

            if whole_interval >= itemize(min_whole_interval):
                patterns.append(
                    Pattern(prefix + [pair], support, whole_interval))

    return patterns


def mine(sequences: List[List[Item]],
         itemize: Callable[[int], int],
         min_support: Union[int, float],
         min_interval: int = 0,
         max_interval: int = inf,
         min_whole_interval: int = 0,
         max_whole_interval: float = inf):
    """Run generalized sequential pattern mining with interval algorithm.

    Args:
        sequences: sequences to mine
        itemize: itemize function
        min_support: minimal count (int) of pattern occurence 
            or percentage (float)
        min_interval (int): minimum interval between each adjacent items,
        max_interval (int): maximum interval between each adjacent items
        min_whole_interval (int): minimum interval from begining to the end, 
            base on itemized interval (to be updated).
        max_whole_interval (int): maximum interval from begining to the end, 
            base on itemized interval (to be updated).
    """
    if isinstance(min_support, float):
        if not 0 <= min_support <= 1:
            raise ValueError(f'0 <= min_support <= 1 ({min_support=})')

        min_support = ceil(len(sequences) * min_support)

    counter = Counter()
    for sequence in sequences:
        elements = set()
        for item in sequence:
            elements.update(item.elements)

        counter.update(elements)

    patterns = []
    for element, support in counter.items():
        if support >= min_support:
            pair = Pair(0, element)

            if pair.interval >= min_whole_interval:
                patterns.append(Pattern([pair], support, 0))

            if (projected_db := project_level1(sequences, pair, itemize)):
                patterns.extend(
                    mine_subpatterns(projected_db, [pair], itemize,
                                     min_support, min_interval, max_interval,
                                     min_whole_interval, max_whole_interval))

    return patterns
