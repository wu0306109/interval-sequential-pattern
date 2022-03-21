from typing import Callable, Generator, Hashable, List, NamedTuple, Set


class Item(NamedTuple):
    """ Item of sequence.
    
    interval: interval from zero without itemize transformation
    """

    interval: int
    elements: Set[Hashable]


class Pair(NamedTuple):
    """ Pair of sequence.

    interval: interval from previous pair after itemize transformation
    """

    interval: int
    element: Hashable


def generate_postfixes(sequence: List[Item],
                       projector: Pair,
                       itemize: Callable[[int], int],
                       level1: bool = False) -> Generator[Item, None, None]:
    """ Yield postfixs according to projector.

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
