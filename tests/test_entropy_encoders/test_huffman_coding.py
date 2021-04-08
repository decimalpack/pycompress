from collections import Counter
from typing import List, Sequence

import hypothesis.strategies as st
from entropy_encoders import huffman_coding
from hypothesis import assume, given

text_strategy = st.text(st.characters(), max_size=10**9)


@given(st.lists(text_strategy,))
def test_list_of_strings(symbol_list: List):
    assume(len(set(symbol_list))>=2)
    enc = huffman_coding.encode(symbol_list)
    dec = huffman_coding.decode(enc)
    assert symbol_list == dec
