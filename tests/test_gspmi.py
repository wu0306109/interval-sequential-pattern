from sequential_pattern.gspmi import (Item, Pair, generate_postfixes,
                                      project_level1, project)


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