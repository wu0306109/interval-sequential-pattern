from collections import Counter
from math import inf, isinf
from typing import Generator, Hashable, List, NamedTuple, Set, Tuple, Union
from multiprocessing import Pool

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


_BuildInSequence = List[Tuple[int, Set[Hashable]]]
_Sequence = List[Item]


def transform(sequences: List[_BuildInSequence]) -> List[List[Item]]:
    """Transform sequences with Python build-in types
    to fit the format using by GSPMI."""
    return [[Item(interval, elements) for interval, elements in sequence]
            for sequence in sequences]


class Gspmi:
    """Algorithm object for 
    Generailized Sequential Pattern Mining with Interval.

    Attributes:
        itemize: itemize function
        min_support: minimal count of pattern occurence.
        min_interval: minimum interval between each adjacent items
        max_interval: maximum interval between each adjacent items
        min_whole_interval: minimum interval from begining to the end, 
            base on itemized interval (to be updated)
        max_whole_interval: maximum interval from begining to the end, 
            base on itemized interval (to be updated).
        multiprocessing: whether to run with multiprocessing, if ture, 
            inputed itemize must be picklizeable, please refer: 
            https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled
        n_processes: number of worker processes to use 
            (valid only when multiprocessing is true). If processes 
            is None then the number returned by os.cpu_count() is used.
    """

    def __init__(self,
                 itemize: Itemize,
                 min_support: int,
                 min_interval: int = 0,
                 max_interval: int = inf,
                 min_whole_interval: int = 0,
                 max_whole_interval: int = inf,
                 multiprocessing: bool = False,
                 n_processes: int = None):
        self.itemize = itemize
        self.min_support = min_support
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.min_whole_interval = min_whole_interval
        self.max_whole_interval = max_whole_interval

        self.multiprocessing = multiprocessing
        self.n_processes = n_processes

    def _generate_postfixes(
            self,
            sequence: _Sequence,
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

    def _project_level1(self, sequences: List[_Sequence],
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

    def _project(self, projected_db: List[List[_Sequence]],
                 projector: Pair) -> List[List[_Sequence]]:
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

    def _mine_subpatterns(self, projected_db: List[List[_Sequence]],
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

    def _mine_subpatterns_level1(self, sequences: List[_Sequence],
                                 element: Hashable,
                                 support: int) -> List[Pattern]:
        patterns = []

        if support >= self.min_support:
            pair = Pair(0, element)
            if pair.interval >= self.min_whole_interval:
                patterns.append(Pattern([pair], support, 0))

            projected_db = self._project_level1(sequences, pair)
            patterns.extend(self._mine_subpatterns(projected_db, [pair]))

        return patterns

    def mine_patterns(
        self, sequences: Union[List[_Sequence], List[_BuildInSequence]]
    ) -> List[Pattern]:
        """Run the algorithm and mine patterns.
        
        Transform sequences if passing with build-in types.
        """
        if len(sequences) > 0 and not isinstance(sequences[0][0], Item):
            sequences = transform(sequences)

        counter = Counter()
        for sequence in sequences:
            elements = set()
            for item in sequence:
                elements.update(item.elements)

            counter.update(elements)

        patterns = []

        if not self.multiprocessing:
            for element, support in counter.items():
                subpatterns = self._mine_subpatterns_level1(
                    sequences, element, support)
                patterns.extend(subpatterns)
        else:
            results = []
            with Pool(self.n_processes) as pool:
                for element, support in counter.items():
                    result = pool.apply_async(self._mine_subpatterns_level1,
                                              (sequences, element, support))
                    results.append(result)

                for result in results:
                    patterns.extend(result.get())

        return patterns
