import itertools as it

import numpy as np

from .util import _parse_prefix_free


class FixedToVariableCode:
    r"""
    Binary, prefix-free, fixed-to-variable length code. Let :math:`\mathcal{X} = \{0, 1, \ldots, |\mathcal{X} - 1| \}` be the alphabet of some discrete source. A *binary fixed-to-variable length code* of *source block size* :math:`k` is defined by an *encoding mapping* :math:`\mathrm{Enc} : \mathcal{X}^k \to \{ 0, 1 \}^+`, where :math:`\{ 0, 1 \}^+` denotes the set of all finite-length, non-empty binary strings. The elements in the image of :math:`\mathrm{Enc}` are called *codewords*.

    Warning:

        Only *prefix-free* codes are considered, in which no codeword is a prefix of any other codeword.
    """

    def __init__(self, codewords, source_cardinality=None):
        r"""
        Constructor for the class.

        Parameters:

            codewords (:obj:`list` of :obj:`tuple` of :obj:`int`): The codewords of the code. Must be a list of length :math:`|\mathcal{X}|^k` containing tuples of integers in :math:`\{ 0, 1 \}`. The tuple in position :math:`i` of :code:`codewords` should be equal to :math:`\mathrm{Enc}(u)`, where :math:`u` is the :math:`i`-th element in the lexicographic ordering of :math:`\mathcal{X}^k`.

            source_cardinality (:obj:`int`, optional): The cardinality :math:`|\mathcal{X}|` of the source alphabet. The default value is :code:`len(codewords)`, yielding a source block size :math:`k = 1`.

        Note:

            The source block size :math:`k` is inferred from :code:`codewords` and :code:`source_cardinality`.

        Examples:

            >>> code = komm.FixedToVariableCode(codewords=[(0,), (1,0), (1,1)])
            >>> (code.source_cardinality, code.source_block_size)
            (3, 1)
            >>> pprint(code.enc_mapping)
            {(0,): (0,), (1,): (1, 0), (2,): (1, 1)}
            >>> pprint(code.dec_mapping)
            {(0,): (0,), (1, 0): (1,), (1, 1): (2,)}

            >>> code = komm.FixedToVariableCode(codewords=[(0,), (1,0,0), (1,1), (1,0,1)], source_cardinality=2)
            >>> (code.source_cardinality, code.source_block_size)
            (2, 2)
            >>> pprint(code.enc_mapping)
            {(0, 0): (0,), (0, 1): (1, 0, 0), (1, 0): (1, 1), (1, 1): (1, 0, 1)}
            >>> pprint(code.dec_mapping)
            {(0,): (0, 0), (1, 0, 0): (0, 1), (1, 0, 1): (1, 1), (1, 1): (1, 0)}
        """
        # TODO: Assert prefix-free
        self._codewords = codewords
        self._source_cardinality = len(codewords) if source_cardinality is None else int(source_cardinality)
        self._source_block_size = 1
        while self._source_cardinality**self._source_block_size < len(codewords):
            self._source_block_size += 1

        if self._source_cardinality**self._source_block_size != len(codewords):
            raise ValueError("Invalid number of codewords")

        self._enc_mapping = {}
        self._dec_mapping = {}
        for symbols, bits in zip(
            it.product(range(self._source_cardinality), repeat=self._source_block_size), codewords
        ):
            self._enc_mapping[symbols] = tuple(bits)
            self._dec_mapping[tuple(bits)] = symbols

    @property
    def source_cardinality(self):
        r"""
        The cardinality :math:`|\mathcal{X}|` of the source alphabet.
        """
        return self._source_cardinality

    @property
    def source_block_size(self):
        r"""
        The source block size :math:`k`.
        """
        return self._source_block_size

    @property
    def enc_mapping(self):
        r"""
        The encoding mapping :math:`\mathrm{Enc}` of the code.
        """
        return self._enc_mapping

    @property
    def dec_mapping(self):
        r"""
        The decoding mapping :math:`\mathrm{Dec}` of the code.
        """
        return self._dec_mapping

    def rate(self, pmf):
        r"""
        Computes the expected rate :math:`R` of the code, assuming a given :term:`pmf`. This quantity is given by

        .. math::
           R = \frac{\bar{n}}{k},

        where :math:`\bar{n}` is the expected codeword length, assuming :term:`i.i.d.` source symbols drawn from :math:`p_X`, and :math:`k` is the source block size. It is measured in bits per source symbol.

        Parameters:

            pmf (1D-array of :obj:`float`): The (first-order) probability mass function :math:`p_X` to be assumed.

        Returns:

            rate (:obj:`float`): The expected rate :math:`R` of the code.

        Examples:

            >>> code = komm.FixedToVariableCode([(0,), (1,0), (1,1)])
            >>> code.rate([0.5, 0.25, 0.25])
            1.5
        """
        probabilities = np.array([np.prod(ps) for ps in it.product(pmf, repeat=self._source_block_size)])
        lengths = [len(bits) for bits in self._codewords]
        return np.dot(lengths, probabilities) / self._source_block_size

    def encode(self, symbol_sequence):
        r"""
        Encodes a sequence of symbols to its corresponding sequence of bits.

        Parameters:

            symbol_sequence (1D-array of :obj:`int`): The sequence of symbols to be encoded. Must be a 1D-array with elements in :math:`\mathcal{X} = \{0, 1, \ldots, |\mathcal{X} - 1| \}`. Its length must be a multiple of :math:`k`.

        Returns:

            bit_sequence (1D-array of :obj:`int`): The sequence of bits corresponding to :code:`symbol_sequence`.

        Examples:

            >>> code = komm.FixedToVariableCode([(0,), (1,0), (1,1)])
            >>> code.encode([1, 0, 1, 0, 2, 0])
            array([1, 0, 0, 1, 0, 0, 1, 1, 0])
        """
        symbols_reshaped = np.reshape(symbol_sequence, newshape=(-1, self._source_block_size))
        return np.concatenate([self._enc_mapping[tuple(symbols)] for symbols in symbols_reshaped])

    def decode(self, bit_sequence):
        r"""
        Decodes a sequence of bits to its corresponding sequence of symbols.

        Parameters:

            bit_sequence (1D-array of :obj:`int`): The sequence of bits to be decoded. Must be a 1D-array with elements in :math:`\{ 0, 1 \}`.

        Returns:

            symbol_sequence (1D-array of :obj:`int`): The sequence of symbols corresponding to :code:`bits`.

        Examples:

            >>> code = komm.FixedToVariableCode([(0,), (1,0), (1,1)])
            >>> code.decode([1, 0, 0, 1, 0, 0, 1, 1, 0])
            array([1, 0, 1, 0, 2, 0])
        """
        return np.array(_parse_prefix_free(bit_sequence, self._dec_mapping))

    def __repr__(self):
        args = "codewords={}".format(self._codewords)
        return "{}({})".format(self.__class__.__name__, args)
