from typing import Callable, List

import pandas as pd
import pytest
from intseqpat.gspmi import Item, Pair, Pattern, generate_postfixes, gspmi, postfix, project


@pytest.fixture
def sequences() -> List[List[Item]]:
    return [
        [
            Item(0, {'a'}),
            Item(86400, {'a', 'b', 'c'}),
            Item(259200, {'a', 'c'}),
        ],
        [
            Item(0, {'a', 'd'}),
            Item(259200, {'c'}),
        ],
        [
            Item(0, {'a', 'e', 'f'}),
            Item(172800, {'a', 'b'}),
        ],
    ]


class TestItem:

    def test_exclude(self) -> None:
        item = Item(0, {'g', 'c', 'd', 'a', 'b', 'e', 'f'})
        assert item.exclude('g').elements == set()
        assert item.exclude('f').elements == {'g'}
        assert item.exclude('b').elements == {'g', 'c', 'd', 'e', 'f'}

    def test_minus(self) -> None:
        item = Item(100, {})
        assert item.minus(0).interval == 100
        assert item.minus(50).interval == 50
        assert item.minus(100).interval == 0


def test_generate_postfixes(sequences: List[List[Item]]) -> None:
    assert generate_postfixes(sequences[0], 'a') == [
        [
            Item(86400, {'a', 'b', 'c'}),
            Item(259200, {'a', 'c'}),
        ],
        [
            Item(0, {'b', 'c'}),
            Item(172800, {'a', 'c'}),
        ],
        [
            Item(0, {'c'}),
        ],
    ]


def test_postfix() -> None:
    assert postfix(
        sequence=[
            Item(0, {'b', 'c'}),
            Item(172800, {'a', 'c'}),
        ],
        projector=Pair(0, 'b'),
        itemize=lambda t: t // 86400,
    ) == [
        Item(0, {'c'}),
        Item(172800, {'a', 'c'}),
    ]


def test_project():
    sequences = pd.Series({
        (0, 0): [
            Item(86400, {'a', 'b', 'c'}),
            Item(259200, {'a', 'c'}),
        ],
        (0, 1): [
            Item(0, {'b', 'c'}),
            Item(172800, {'a', 'c'}),
        ],
        (0, 2): [
            Item(0, {'c'}),
        ],
        (1, 0): [
            Item(0, {'d'}),
            Item(259200, {'c'}),
        ],
        (2, 0): [
            Item(0, {'e', 'f'}),
            Item(172800, {'a', 'b'}),
        ],
        (2, 1): [
            Item(0, {'b'}),
        ],
    })
    project(
        sequences=sequences,
        itemize=lambda t: t // 86400,
        prefix=[Pair(0, {'a'})],
        min_support=2,
    ) == [
        Pattern(
            sequence=[Pair(0, 'a'), Pair(0, 'b')],
            support=2,
            count=2,
            whole_interval=0,
        ),
    ]
