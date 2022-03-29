from math import inf, log2

from seqpat.gspmi import (Item, Pair, Pattern, generate_postfixes, mine,
                          mine_subpatterns, project, project_level1)


def test_generate_postfixes():
    sequence = [
        Item(0, {'a'}),
        Item(86400, {'a', 'b', 'c'}),
        Item(259200, {'a', 'c'}),
    ]
    pair = Pair(0, 'a')
    itemize = lambda interval: interval // 86400
    expected = [
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
    result = list(generate_postfixes(sequence, pair, itemize, level1=True))
    assert result == expected

    sequence = [
        Item(0, {'b', 'c'}),
        Item(172800, {'a', 'c'}),
    ]
    pair = Pair(0, 'b')
    expected = [
        Item(0, {'c'}),
        Item(172800, {'a', 'c'}),
    ]
    result = next(generate_postfixes(sequence, pair, itemize), None)
    assert result == expected


def test_project_level1():
    sequences = [
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
    projector = Pair(0, 'a')
    itemize = lambda interval: interval // 86400
    expected = [
        [
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
        ],
        [
            [
                Item(0, {'d'}),
                Item(259200, {'c'}),
            ],
        ],
        [
            [
                Item(0, {'e', 'f'}),
                Item(172800, {'a', 'b'}),
            ],
            [
                Item(0, {'b'}),
            ],
        ],
    ]
    result = project_level1(sequences, projector, itemize)
    assert result == expected


def test_project():
    projeced_db = [
        [
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
        ],
        [
            [
                Item(0, {'d'}),
                Item(259200, {'c'}),
            ],
        ],
        [
            [
                Item(0, {'e', 'f'}),
                Item(172800, {'a', 'b'}),
            ],
            [
                Item(0, {'b'}),
            ],
        ],
    ]
    projector = Pair(0, 'b')
    itemize = lambda interval: interval // 86400
    expected = [
        [
            [
                Item(0, {'c'}),
                Item(172800, {'a', 'c'}),
            ],
        ],
    ]
    result = project(projeced_db, projector, itemize)
    assert result == expected


def test_mine_subpatterns():
    projected_db = [
        [
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
        ],
        [
            [
                Item(0, {'d'}),
                Item(259200, {'c'}),
            ],
        ],
        [
            [
                Item(0, {'e', 'f'}),
                Item(172800, {'a', 'b'}),
            ],
            [
                Item(0, {'b'}),
            ],
        ],
    ]
    prefix = [
        Pair(0, 'a'),
    ]
    itemize = lambda interval: interval // 86400
    min_support = 2
    min_interval = 0
    max_interval = 172800
    min_whole_interval = 0
    max_whole_interval = inf
    expected = [
        Pattern([Pair(0, 'a'), Pair(0, 'b')], 2, 0),
        Pattern([Pair(0, 'a'), Pair(2, 'a')], 2, 2),
    ]
    result = mine_subpatterns(projected_db, prefix, itemize, min_support,
                              min_interval, max_interval, min_whole_interval,
                              max_whole_interval)
    assert sorted(result) == sorted(expected)


def test_mine():
    sequence_db = [
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
    itemize = lambda interval: interval // 86400
    min_support = 0.5
    max_interval = 172800
    expected = [
        Pattern([Pair(0, 'a')], 3, 0),
        Pattern([Pair(0, 'a'), Pair(0, 'b')], 2, 0),
        Pattern([Pair(0, 'a'), Pair(2, 'a')], 2, 2),
        Pattern([Pair(0, 'b')], 2, 0),
        Pattern([Pair(0, 'c')], 2, 0),
    ]
    result = mine(sequence_db, itemize, min_support, max_interval=max_interval)
    assert sorted(result) == sorted(expected)


def test_complex_sequences():
    # Only make sure every found patterns is actually exists.
    a = 'a'
    b = 'b'
    c = 'c'
    sequences = [
        [
            Item(0, {a}),
            Item(1, {a, b, c}),
            Item(4, {a}),
            Item(12, {b, c}),
            Item(44, {a, b}),
            Item(45, {a, b}),
            Item(67, {b, c}),
        ],
        [
            Item(0, {a}),
            Item(1, {a}),
            Item(7, {a, b}),
            Item(14, {a, b, c}),
            Item(77, {a}),
            Item(78, {b}),
        ],
        [
            Item(0, {a}),
            Item(6, {a, b, c}),
            Item(10, {b, c}),
            Item(66, {a, c}),
            Item(67, {b, c}),
        ],
        [
            Item(0, {a}),
            Item(1, {a, b, c}),
            Item(79, {a, b}),
        ],
        [
            Item(0, {a}),
            Item(1, {a, b, c}),
            Item(127, {a, b}),
        ],
    ]
    itemize = lambda t: int(log2(t + 1))
    patterns = mine(sequences, itemize, min_support=2)

    def project(projector, postfix):
        # Return projected postfix if exists, otherwise return none
        for i, (interval, elements) in enumerate(postfix):
            if (projector.interval == itemize(interval)
                    and projector.element in elements):
                return [Item(ii - interval, ee) for ii, ee in postfix[i:]]
        else:
            return None

    def match_postfix(pattern, postfix):
        for pair in pattern.sequence:
            if (postfix := project(pair, postfix)) is None:
                return False
        else:
            return True

    def match_sequence(pattern, sequence):
        first = pattern.sequence[0]

        for i, (interval, elements) in enumerate(sequence):
            if first.element in elements:
                postfix = [Item(i - interval, e) for i, e in sequence[i:]]

                if match_postfix(pattern, postfix):
                    return True

        else:
            return False

    for pattern in patterns:
        count = sum(match_sequence(pattern, s) for s in sequences)

        assert count == pattern.support
