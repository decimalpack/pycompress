import heapq
from collections import namedtuple
from dataclasses import dataclass, field
from typing import Any, Counter, Dict, List

HuffmanCodeReturn = namedtuple("HuffmanCodeReturn", "lookup_table bit_string")


@dataclass(order=True)
class __Node:
    freq: int
    item: Any = field(compare=False)


def __construct_tree(frequency_table: Counter[str]) -> __Node:
    """
    Construct a huffman tree from the frequency table using heapq and return the root node

    Uses the following dataclass for Priority Queue
    @dataclass(order=True)
    class __Node:
        freq: int
        item: Any = field(compare=False)

    Internal nodes are __Node's of form:
        (Frequency, (left_child, right_child))
    
    Leaf nodes are __Node's of form:
        (Frequency,symbol)


    Parameters
    ----------
    frequency_table : Counter

    Returns
    -------
    __Node
        The root node
    """
    total = sum(frequency_table.values())
    huffman_tree = [
        __Node(frequency, (symbol, ))
        for symbol, frequency in frequency_table.items()
    ]
    heapq.heapify(huffman_tree)

    mx_count = 0
    while mx_count != total:
        l, r = heapq.heappop(huffman_tree), heapq.heappop(huffman_tree)
        new_freq = l.freq + r.freq
        heapq.heappush(huffman_tree, __Node(new_freq, (l, r)))
        mx_count = max(mx_count, new_freq)
    return huffman_tree[0]


def __create_lookup_table(root: __Node) -> Dict[str, str]:
    """
    Given the root node of huffman tree, uses dfs to assign code words (bit string) to symbols

    Parameters
    ----------
    root : __Node
        The root node of huffman tree

    Returns
    -------
    Dict[str, str]
        A dictionary mapping symbols to bit strings
    """
    lookup_table: Dict[str, str] = {}

    def dfs(root, code=""):
        if not isinstance(root.item[0], __Node):
            lookup_table[root.item[0]] = code
        else:
            l, r = root.item
            dfs(l, code + "0")
            dfs(r, code + "1")

    dfs(root)
    return lookup_table


def encode(symbol_list: List[str],
           frequency_table: Counter[str] = None) -> HuffmanCodeReturn:
    """
    Given a list of symbol, constructs huffman tree and returns a named tuple containing:
        - The lookup table 
        - The bit_string

    Parameters
    ----------
    input_data : List
        List of symbols
    frequency_table : Counter, optional
        A custom frequency table, by default None
        If not provided, it will calculated from the symbol_list

    Returns
    -------
    HuffmanCodeReturn
        = namedtuple("HuffmanCodeReturn", "lookup_table bit_string")
    """
    # No need for probabilities as only comparison is required
    if frequency_table is None: frequency_table = Counter(symbol_list)

    assert len(frequency_table) >= 2, "Atleast 2 symbols required"
    root = __construct_tree(frequency_table)
    lookup_table = __create_lookup_table(root)

    bit_string = "".join(lookup_table[symbol] for symbol in symbol_list)
    return HuffmanCodeReturn(lookup_table=lookup_table, bit_string=bit_string)


def decode(encoded: HuffmanCodeReturn) -> List[str]:
    """
    Decode an HuffmanCoded sequence and return a list of symbols
    Translate the bit_str to a list of symbols
    Parameters
    ----------
    encoded : HuffmanCodeReturn
        = namedtuple("HuffmanCodeReturn", "lookup_table bit_string"),

    Returns
    -------
    List[str]
        The list of symbols
    """    
    lookup_table = {
        bit_str: symbol
        for symbol, bit_str in encoded.lookup_table.items()
    }
    output = []
    prefix = ""
    for bit in encoded.bit_string:
        prefix += bit
        symbol = lookup_table.get(prefix)
        if  symbol is not None:
            output.append(symbol)
            prefix = ""
    return output
