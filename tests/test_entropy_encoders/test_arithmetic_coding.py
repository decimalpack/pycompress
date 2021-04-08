from typing import List, Sequence

import hypothesis.strategies as st
from entropy_encoders import arithmetic_coding
from hypothesis import given

EOF = "\n"
text_strategy = st.text(st.characters(blacklist_characters=EOF),
                        max_size=10**9)


@given(st.lists(text_strategy))
def test_list_of_strings(symbol_list: List):
    symbol_list += EOF
    enc = arithmetic_coding.encode(symbol_list, EOF)
    dec = arithmetic_coding.decode(enc)
    assert symbol_list == dec


@st.composite
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
def test_list_of_hashables(symbol_list: List):
    symbol_list += EOF
    enc = arithmetic_coding.encode(symbol_list, EOF)
    dec = arithmetic_coding.decode(enc)
    assert symbol_list == dec


@given(st.from_type(Sequence))
def test_sequence(seq):
    seq += EOF
    enc = arithmetic_coding.encode(seq, EOF)
    dec = arithmetic_coding.decode(enc)
    assert seq == dec


def test_handwritten():
    pt = {
        "R": 0.4,
        "G": 0.5,
        "B": 0.1,
    }
    string = list("GGB")
    enc = arithmetic_coding.encode(string, "B", probability_table=pt)
    assert enc.decimal == "83"
    dec = arithmetic_coding.decode(enc)
    if isinstance(string, str):
        dec = "".join(dec)
    assert string == dec
