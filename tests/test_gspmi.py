from math import log2

from seqpat.gspmi import Gspmi, Item, Pair, Pattern


class TestGspmi:

    def test_basic_mine_patterns(self):
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
        gspmi = Gspmi(itemize=lambda i: i // 86400,
                      min_support=2,
                      max_interval=172800)
        expected = [
            Pattern([Pair(0, 'a')], 3, 0),
            Pattern([Pair(0, 'b')], 2, 0),
            Pattern([Pair(0, 'c')], 2, 0),
            Pattern([Pair(0, 'a'), Pair(0, 'b')], 2, 0),
            Pattern([Pair(0, 'a'), Pair(2, 'a')], 2, 2),
        ]

        result = gspmi.mine_patterns(sequences)
        assert sorted(result) == sorted(expected)

    def test_complex_mine_patterns(self):
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
        gspmi = Gspmi(itemize=itemize, min_support=2)
        patterns = gspmi.mine_patterns(sequences)

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
