import numpy as np

from .Modulation import Modulation


class RealModulation(Modulation):
    r"""
    General real modulation scheme. A *real modulation scheme* of order :math:`M` is defined by a *constellation* :math:`\mathcal{S}`, which is an ordered subset (a list) of real numbers, with :math:`|\mathcal{S}| = M`, and a *binary labeling* :math:`\mathcal{Q}`, which is a permutation of :math:`[0: M)`. The order :math:`M` of the modulation must be a power of :math:`2`.
    """

    def __init__(self, constellation, labeling):
        r"""
        Constructor for the class.

        Parameters:

            constellation (1D-array of :obj:`complex`): The constellation :math:`\mathcal{S}` of the modulation. Must be a 1D-array containing :math:`M` real numbers.

            labeling (1D-array of :obj:`int`): The binary labeling :math:`\mathcal{Q}` of the modulation. Must be a 1D-array of integers corresponding to a permutation of :math:`[0 : M)`.

        Examples:

            >>> mod = komm.RealModulation(constellation=[-0.5, 0, 0.5, 2], labeling=[0, 1, 3, 2])
            >>> mod.constellation
            array([-0.5,  0. ,  0.5,  2. ])
            >>> mod.modulate([0, 0, 1, 1, 0, 0, 1, 0, 1, 0])
            array([-0.5,  0.5, -0.5,  0. ,  0. ])
        """
        super().__init__(np.array(constellation, dtype=float), labeling)
