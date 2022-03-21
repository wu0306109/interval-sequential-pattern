from sequential_pattern_mining.gspmi import generate_postfixes, Item, Pair


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