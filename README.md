# Interval-extended Sequence Pattern Mining Library

## Installation

Come to [Releases](https://github.com/wu0306109/interval-sequential-pattern/releases) first to download a version and decompress it.

```bash
cd interval-sequential-pattern-x.x.x
python3 -m pip install .
```

## Quick Start

```python
from intseqpat.gspmi import Gspmi

a, b, c, d, e, f = 'a', 'b', 'c', 'd', 'e', 'f'
sequences = [
    [(0, {a}), (86400, {a, b, c}), (259200, {a, c})],
    [(0, {a, d}), (259200, {c})],
    [(0, {a, e, f}), (172800, {a, b})],
]

gspmi = Gspmi(itemize=lambda i: i // 86400,
                min_support=2,
                max_interval=172800)
result = gspmi.mine_patterns(sequences)
```

## References

1. Hirate, Y., & Yamana, H. (2006). Generalized sequential pattern mining with item intervals. Journal of Computers, 1(3), 51-60. https://doi.org/10.4304/jcp.1.3.51-60
