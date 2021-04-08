import bisect
import decimal
from collections import namedtuple
from decimal import Decimal
from typing import Counter, Dict, Hashable, List, Tuple

ArithmeticEncodingReturn = namedtuple(
    "ArithmeticEncodingReturn", "decimal probability_table end_of_sequence")


def __init_range_table(probability_table):
    range_table = {}
    prev = Decimal(0)
    for symbol, probability in probability_table.items():
        range_table[symbol] = [prev, prev + probability]
        prev += probability
    return range_table


def __update_range_table(range_table: Dict[Hashable, List[Decimal]],
                         probability_table: Dict[Hashable, Decimal],
                         symbol: Hashable) -> Tuple[Decimal, Decimal]:
    """
    Update the range_table (in place) to width of symbol

    Parameters
    ----------
    range_table : Dict[Hashable, List[Decimal]]
        A Dictionary mapping symbols to ranges:

        Example:
        {
            "A":[Decimal(0.4), Decimal(0.5)],
            "B":[Decimal(0.5), Decimal(0.7)],
        }

    probability_table : Dict[Hashable, Decimal]

    symbol : Hashable

    Returns
    -------
    Tuple[Decimal, Decimal]
        [description]
    """
    lower, upper = range_table[symbol]
    width = upper - lower
    prev = lower
    for symbol, probability in probability_table.items():
        range_table[symbol] = [prev, prev + probability * width]
        prev += probability * width
        upper = prev
    return lower, upper


def __minimize_entropy(lower: Decimal, upper: Decimal) -> Decimal:
    """
    Given lower range and upper range, this function finds an x, lower<=x<upper
    Such that it has minimum length

    Parameters
    ----------
    lower : Decimal
    upper : Decimal

    Returns
    -------
    Decimal
    """
    jump = Decimal("0.1")
    while True:
        start = lower.quantize(jump)
        while start < upper:
            if lower <= start < upper: return start
            start += jump
        jump /= Decimal(10)


def __create_probability_table(symbol_list):
    frequency_table = Counter(symbol_list)
    N = sum(frequency_table.values())
    assert N != 0

    return {
        symbol: Decimal(freq) / N
        for symbol, freq in frequency_table.items()
    }


def encode(symbol_list: List[Hashable],
           end_of_sequence: str,
           precision: int = 100,
           probability_table: Dict = None) -> ArithmeticEncodingReturn:
    """
    Uses the Arithmetic Coding algorithm
    

    ### Note
    The method relies on 'precision' of Decimal from the python Standard Library.

    If data is large, complete decoding might not be possible

    Parameters
    ----------
    symbol_list : List[Hashable]
        List of symbols
    end_of_sequence : str
        A special character that only occurs at end_of_sequences.
        Both probability_table (if given) and input_data must have this table
    precision : int, optional, by default 100
        The precision of Decimal, will be set as:
        getcontext().prec = precision
    probability_table : Dict, optional, by default None
        A dictionary mapping symbols to their probabilities

        Example:
            {
                "R": 0.4,
                "G": 0.5,
                "B": 0.1,
            }

        If None, one will be calculated for you by using the frequency of input data

    Returns
    -------
    ArithmeticEncdodingReturn
        = namedtuple("ArithmeticEncodingReturn", "decimal probability_table end_of_sequence")
        
        decimal = A string containing the decimal representation of a fraction, with prefix "0." removed
        probability_table = Same as input, with floats casted to Decimal
        end_of_sequence = Same as input
    """
    assert end_of_sequence in symbol_list
    decimal.getcontext().prec = precision

    if probability_table is None:
        probability_table = __create_probability_table(symbol_list)
    else:
        # Since the user has given probability_table, it might not contain end_of_sequence character
        assert end_of_sequence in probability_table
        probability_table = {
            k: Decimal(str(v))
            for k, v in probability_table.items()
        }
    # Check if sum of probabilities is 1
    assert abs(sum(probability_table.values()) -
               Decimal("1")) < Decimal("1e-5")

    range_table = __init_range_table(probability_table)
    for symbol in symbol_list:
        lower, upper = __update_range_table(range_table, probability_table,
                                            symbol)
    return ArithmeticEncodingReturn(
        str(__minimize_entropy(lower, upper))[2:], probability_table,
        end_of_sequence)


def decode(encoded: ArithmeticEncodingReturn,
           precision: int = 100) -> List[Hashable]:
    """
    Decode an Arithmetic Encoded sequence and return a list of symbols
    # Warning:
        If precision is too low, the sequence will not reach end_of_sequence and 
        hence run into an infinite loop
    Parameters
    ----------
    encoded : ArithmeticEncodingReturn
        ArithmeticEncodingReturn = namedtuple(
            "ArithmeticEncodingReturn", "decimal probability_table end_of_sequence")
    precision : int
        The precision of Decimal, will be set as:
        getcontext().prec = precision

    Returns
    -------
    List[Hashable]
        List containing symbols (including end_of_sequence) from encoded.probability_table
    """
    decimal.getcontext().prec = precision
    fraction = Decimal("0." + encoded.decimal)
    probability_table = encoded.probability_table

    range_lower = []  # Stores the CDF
    range_symbol = []  # Stores the corresponding symbol
    prev = Decimal(0)
    for symbol, probability in probability_table.items():
        range_lower.append(prev)
        range_symbol.append(symbol)
        prev += probability

    output = []
    symbol = None
    while symbol != encoded.end_of_sequence:
        # Use Binary Search to find closest symbol
        v = bisect.bisect_right(range_lower, fraction) - 1
        symbol = range_symbol[v]
        output.append(symbol)
        fraction -= range_lower[v]
        fraction /= probability_table[symbol]
    return output
