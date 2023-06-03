import numpy as np

from .Pulse import Pulse


class RaisedCosinePulse(Pulse):
    r"""
    Raised cosine pulse. It is a formatting pulse (:class:`FormattingPulse`) with impulse response given by

    .. math::

        h(t) = \operatorname{sinc}(t) \frac{\cos(\pi \alpha t)}{1 - (2 \alpha t)^2},

    where :math:`\alpha` is the *roll-off factor*. The raised cosine pulse is depicted below for :math:`\alpha = 0.25`, and for :math:`\alpha = 0.75`.

    .. rst-class:: centered

       |fig1| |quad| |quad| |quad| |fig2|

    .. |fig1| image:: figures/pulse_raised_cosine_25.png
       :alt: Raised cosine pulse with roll-off factor 0.25

    .. |fig2| image:: figures/pulse_raised_cosine_75.png
       :alt: Raised cosine pulse with roll-off factor 0.75

    .. |quad| unicode:: 0x2001
       :trim:

    For  :math:`\alpha = 0`, the raised cosine pulse reduces to the sinc pulse (:class:`SincPulse`).
    """

    def __init__(self, rolloff, length_in_symbols):
        r"""
        Constructor for the class. It expects the following parameters:

        :code:`rolloff` : :obj:`float`
            The roll-off factor :math:`\alpha` of the pulse. Must satisfy :math:`0 \leq \alpha \leq 1`.

        :code:`length_in_symbols` : :obj:`int`
            The length (span) of the truncated impulse response, in symbols.

        .. rubric:: Examples

        >>> pulse = komm.RaisedCosinePulse(rolloff=0.25, length_in_symbols=16)

        >>> pulse = komm.RaisedCosinePulse(rolloff=0.75, length_in_symbols=16)
        """
        a = self._rolloff = float(rolloff)
        L = self._length_in_symbols = int(length_in_symbols)

        def impulse_response(t):
            t += 1e-8
            return np.sinc(t) * np.cos(np.pi * a * t) / (1 - (2 * a * t) ** 2)

        def frequency_response(f):
            f1 = (1 - a) / 2
            f2 = (1 + a) / 2
            H = 1.0 * (abs(f) < f1)
            if a > 0:
                H += (f1 < abs(f) < f2) * (0.5 + 0.5 * np.cos((np.pi * (abs(f) - f1)) / (f2 - f1)))
            return H

        super().__init__(impulse_response, frequency_response, interval=(-L / 2, L / 2))

    @property
    def rolloff(self):
        r"""
        The roll-off factor :math:`\alpha` of the pulse. This property is read-only.
        """
        return self._rolloff

    @property
    def length_in_symbols(self):
        r"""
        The length (span) of the truncated impulse response. This property is read-only.
        """
        return self._length_in_symbols

    def __repr__(self):
        args = "rolloff={}, length_in_symbols={}".format(self._rolloff, self._length_in_symbols)
        return "{}({})".format(self.__class__.__name__, args)