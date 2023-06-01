import numpy as np

from .._util import _entropy
from .DiscreteMemorylessChannel import DiscreteMemorylessChannel


class BinarySymmetricChannel(DiscreteMemorylessChannel):
    """
    Binary symmetric channel (BSC). It is a discrete memoryless channel (:obj:`DiscreteMemorylessChannel`) with input and output alphabets given by :math:`\\mathcal{X} = \\mathcal{Y} = \\{ 0, 1 \\}`, and transition probability matrix given by

    .. math::

        p_{Y \\mid X} = \\begin{bmatrix} 1-p & p \\\\ p & 1-p \\end{bmatrix},

    where the parameter :math:`p` is called the *crossover probability* of the channel. Equivalently, a BSC with crossover probability :math:`p` may be defined by

    .. math::
        Y_n = X_n + Z_n,

    where :math:`Z_n` are :term:`i.i.d.` Bernouli random variables with :math:`\\Pr[Z_n = 1] = p`.

    References: :cite:`Cover.Thomas.06` (Sec. 7.1.4)

    To invoke the channel, call the object giving the input signal as parameter (see example below).
    """

    def __init__(self, crossover_probability=0.0):
        """
        Constructor for the class. It expects the following parameter:

        :code:`crossover_probability` : :obj:`float`, optional
            The channel crossover probability :math:`p`. Must satisfy :math:`0 \\leq p \\leq 1`. The default value is :code:`0.0`.

        .. rubric:: Examples

        >>> bsc = komm.BinarySymmetricChannel(0.1)
        >>> x = [0, 1, 1, 1, 0, 0, 0, 0, 0, 1]
        >>> y = bsc(x); y  #doctest:+SKIP
        array([0, 1, 1, 1, 0, 0, 0, 1, 0, 0])
        """
        self.crossover_probability = crossover_probability

    @property
    def crossover_probability(self):
        """
        The crossover probability :math:`p` of the channel. This is a read-and-write property.
        """
        return self._crossover_probability

    @crossover_probability.setter
    def crossover_probability(self, value):
        self._crossover_probability = p = float(value)
        self.transition_matrix = np.array([[1 - p, p], [p, 1 - p]])

    def capacity(self):
        """
        Returns the channel capacity :math:`C`. It is given by :math:`C = 1 - \\mathcal{H}(p)`. See :cite:`Cover.Thomas.06` (Sec. 7.1.4).

        .. rubric:: Examples

        >>> bsc = komm.BinarySymmetricChannel(0.25)
        >>> bsc.capacity()
        0.18872187554086717
        """
        return 1.0 - _entropy(np.array([self._crossover_probability, 1.0 - self._crossover_probability]))

    def __call__(self, input_sequence):
        error_pattern = (np.random.rand(np.size(input_sequence)) < self._crossover_probability).astype(int)
        return (input_sequence + error_pattern) % 2

    def __repr__(self):
        args = "crossover_probability={}".format(self._crossover_probability)
        return "{}({})".format(self.__class__.__name__, args)
