from collections import Counter
from math import inf, isinf
from typing import Generator, Hashable, List, NamedTuple, Set

from seqpat.itemizes import Itemize


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


class Gspmi:
    """Algorithm object for 
    Generailized Sequential Pattern Mining with Interval.

    Attributes:
        itemize: itemize function
        min_support: minimal count (int) of pattern occurence.
        min_interval (int): minimum interval between each adjacent items
        max_interval (int): maximum interval between each adjacent items
        min_whole_interval (int): minimum interval from begining to the end, 
            base on itemized interval (to be updated)
        max_whole_interval (int): maximum interval from begining to the end, 
            base on itemized interval (to be updated).
    """

    def __init__(self,
                 itemize: Itemize,
                 min_support: int,
                 min_interval: int = 0,
                 max_interval: int = inf,
                 min_whole_interval: int = 0,
                 max_whole_interval: int = inf):
        self.itemize = itemize
        self.min_support = min_support
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.min_whole_interval = min_whole_interval
        self.max_whole_interval = max_whole_interval

    def _generate_postfixes(
            self,
            sequence: List[Item],
            projector: Pair,
            level1: bool = False) -> Generator[Item, None, None]:
        """Yield postfixs according to projector.

        The function will yield all element-matched postfix from begining for 
        level1 == True; otherwise only one exactly interval-and-element 
        matched postfix. If no matched, yield nothing.
        """

        def exclude(elements):
            elements = sorted(elements)
            return set(elements[elements.index(projector.element) + 1:])

        for i, (interval, elements) in enumerate(sequence):
            if (projector.element in elements and
                (level1 or self.itemize(interval) == projector.interval)):
                head = exclude(elements)
                postfix = [Item(0, head)] if head else []

                postfix.extend(
                    Item(i - interval, e) for i, e in sequence[i + 1:])
                yield postfix

                if not level1:
                    break

    def _project_level1(self, sequences: List[List[Item]],
                        projector: Pair) -> List[List[List[Item]]]:
        """Project from initial sequence database.

        Each sequence in database will be project to a list of postfix 
        named projected database.
        """
        projected_db = []
        for sequence in sequences:
            if (postfixes := list(
                    self._generate_postfixes(sequence, projector,
                                             level1=True))):
                projected_db.append(postfixes)

        return projected_db

    def _project(self, projected_db: List[List[List[Item]]],
                 projector: Pair) -> List[List[List[Item]]]:
        """Project projected database to the next level by projector."""
        child_projected_db = []
        for sequences in projected_db:
            projected_sequences = []

            for sequence in sequences:
                postfix = next(self._generate_postfixes(sequence, projector),
                               None)
                if postfix:
                    projected_sequences.append(postfix)

            if projected_sequences:
                child_projected_db.append(projected_sequences)

        return child_projected_db

    def _mine_subpatterns(self, projected_db: List[List[List[Item]]],
                          prefix: List[Pair]) -> List[Pattern]:
        """Recursivly mine sub patterns.

        Args:
            prefix: list of projectors generate during projections
        """
        counter = Counter()
        for sequences in projected_db:
            pairs = set()

            for sequence in sequences:
                previous = 0
                for interval, elements in sequence:
                    if self.min_interval <= interval - previous <= self.max_interval:
                        pairs.update(
                            Pair(self.itemize(interval), e) for e in elements)

                    previous = interval

            counter.update(pairs)

        patterns = []
        for pair, support in counter.items():
            whole_interval = sum(i for i, p in prefix) + pair.interval
            if (support >= self.min_support and
                (isinf(self.max_whole_interval)
                 or whole_interval <= self.itemize(self.max_whole_interval))):
                child_projected_db = self._project(projected_db, pair)

                patterns.extend(
                    self._mine_subpatterns(child_projected_db,
                                           prefix + [pair]))

                if whole_interval >= self.itemize(self.min_whole_interval):
                    patterns.append(
                        Pattern(prefix + [pair], support, whole_interval))

        return patterns

    def mine_patterns(self, sequences: List[List[Item]]) -> List[Pattern]:
        """Run the algorithm and mine patterns."""
        counter = Counter()
        for sequence in sequences:
            elements = set()
            for item in sequence:
                elements.update(item.elements)

            counter.update(elements)

        patterns = []
        for element, support in counter.items():
            if support >= self.min_support:
                pair = Pair(0, element)

                if pair.interval >= self.min_whole_interval:
                    patterns.append(Pattern([pair], support, 0))

                if (projected_db := self._project_level1(sequences, pair)):
                    patterns.extend(
                        self._mine_subpatterns(projected_db, [pair]))

        return patterns
