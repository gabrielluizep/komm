import numpy as np

from .Pulse import Pulse


class SincPulse(Pulse):
    r"""
    Sinc pulse. It is a formatting pulse (:class:`FormattingPulse`) with impulse response given by

    .. math::

        h(t) = \operatorname{sinc}(t) = \frac{\sin(\pi t)}{\pi t}.

    The sinc pulse is depicted below.

    .. image:: figures/pulse_sinc.png
       :alt: Sinc pulse
       :align: center
    """

    def __init__(self, length_in_symbols):
        r"""
        Constructor for the class. It expects the following parameters:

        :code:`length_in_symbols` : :obj:`int`
            The length (span) of the truncated impulse response, in symbols.

        .. rubric:: Examples

        >>> pulse = komm.SincPulse(length_in_symbols=64)
        """
        L = self._length_in_symbols = int(length_in_symbols)

        def impulse_response(t):
            return np.sinc(t)

        super().__init__(impulse_response, interval=(-L / 2, L / 2))

    @property
    def length_in_symbols(self):
        r"""
        The length (span) of the truncated impulse response. This property is read-only.
        """
        return self._length_in_symbols

    def __repr__(self):
        args = "length_in_symbols={}".format(self._length_in_symbols)
        return "{}({})".format(self.__class__.__name__, args)