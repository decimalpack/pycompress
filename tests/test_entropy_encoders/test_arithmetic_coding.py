from typing import Any, List, Sequence

import hypothesis.strategies as st
import pytest
from entropy_encoders import arithmetic_coding
from hypothesis import given
from hypothesis.strategies._internal import strategies
from hypothesis.strategies._internal.core import composite

EOF = "$"
text_strategy = st.text(st.characters(blacklist_characters=EOF),
                        max_size=10**9)


@given(text_strategy)
def test_strings(string: str):
    string += EOF
    enc = arithmetic_coding.encode(string, EOF)
    dec = "".join(arithmetic_coding.decode(enc))
    assert string == dec


@given(st.lists(text_strategy))
def test_list_of_strings(lists: str):
    lists += EOF
    print(lists)
    enc = arithmetic_coding.encode(lists, EOF)
    dec = arithmetic_coding.decode(enc)
    if isinstance(lists, str):
        dec = "".join(dec)
    assert lists == dec


@composite
def hashables(draw):
    strats = [
        text_strategy,
        st.integers(),
        st.floats(),
        st.tuples(),
        st.complex_numbers(),
        st.none(),
        st.booleans(),
        st.decimals(allow_nan=False, allow_infinity=False)
    ]
    return list(map(draw, strats))


@given(hashables())
def test_list_of_hashables(lists: str):
    lists += EOF
    enc = arithmetic_coding.encode(lists, EOF)
    dec = arithmetic_coding.decode(enc)
    if isinstance(lists, str):
        dec = "".join(dec)
    assert lists == dec


@given(st.from_type(Sequence))
def test_sequence(seq):
    seq += EOF
    enc = arithmetic_coding.encode(seq, EOF)
    dec = arithmetic_coding.decode(enc)
    if isinstance(seq, str):
        dec = "".join(dec)
    assert seq == dec


def test_handwritten():
    pt = {
        "R": 0.4,
        "G": 0.5,
        "B": 0.1,
    }
    string = "GGB"  
    enc = arithmetic_coding.encode(string, "B", probability_table=pt)
    assert enc.decimal == "83"
    dec = arithmetic_coding.decode(enc)
    if isinstance(string, str):
        dec = "".join(dec)
    assert string == dec
