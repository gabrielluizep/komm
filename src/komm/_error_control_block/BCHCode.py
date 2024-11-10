import operator
from functools import cache, cached_property, reduce

from attrs import frozen

from .._algebra import BinaryPolynomial, FiniteBifield
from .CyclicCode import CyclicCode


@frozen
class BCHCode(CyclicCode):
    r"""
    Bose–Ray-Chaudhuri–Hocquenghem (BCH) code. For given parameters $\mu \geq 2$ and $\delta$ satisfying $2 \leq \delta \leq 2^{\mu} - 1$, a *binary BCH code* is a [cyclic code](/ref/CyclicCode) with generator polynomial given by
    $$
        g(X) = \mathrm{lcm} \left\\{ \phi_1(X), \phi_2(X), \ldots, \phi_{\delta - 1}(X) \right\\},
    $$
    where $\phi_i(X)$ is the minimal polynomial of $\alpha^i$, and $\alpha$ is a primitive element of $\mathrm{GF}(2^\mu)$. The parameter $\delta$ must be a *Bose distance*. The resulting code is denoted by $\bch(\mu, \delta)$, and has the following parameters, where $\delta = 2 \tau + 1$:

    - Length: $n = 2^{\mu} - 1$
    - Dimension: $k \geq n - \mu \tau$
    - Redundancy: $m \leq \mu \tau$
    - Minimum distance: $d \geq \delta$

    Only *narrow-sense* and *primitive* BCH codes are implemented. For more details, see <cite>LC04, Ch. 6</cite> and <cite>HP03, Sec. 5.1</cite>.

    The table below lists the possible values of $\delta$ for $2 \leq \mu \leq 10$.

    | $\mu$ | $n$ |  Bose distances $\delta$ |
    | :-: | :-: | --- |
    | $2$ | $3$ | $3$ |
    | $3$ | $7$ | $3$, $7$ |
    | $4$ | $15$ | $3$, $5$, $7$, $15$ |
    | $5$ | $31$ | $3$, $5$, $7$, $11$, $15$, $31$ |
    | $6$ | $63$ | $3$, $5$, $7$, $9$, $11$, $13$, $15$, $21$, $23$, $27$, $31$, $63$ |
    | $7$ | $127$ | $3$, $5$, $7$, $9$, $11$, $13$, $15$, $19$, $21$, $23$, $27$, $29$, $31$, $43$, $47$, $55$, $63$, $127$ |
    | $8$ | $255$ | $3$, $5$, $7$, $9$, $11$, $13$, $15$, $17$, $19$, $21$, $23$, $25$, $27$, $29$, $31$, $37$, $39$, $43$, $45$, $47$, $51$, $53$, $55$, $59$, $61$, $63$, $85$, $87$, $91$, $95$, $111$, $119$, $127$, $255$ |
    | $9$ | $511$ | $3$, $5$, $7$, $9$, $11$, $13$, $15$, $17$, $19$, $21$, $23$, $25$, $27$, $29$, $31$, $35$, $37$, $39$, $41$, $43$, $45$, $47$, $51$, $53$, $55$, $57$, $59$, $61$, $63$, $73$, $75$, $77$, $79$, $83$, $85$, $87$, $91$, $93$, $95$, $103$, $107$, $109$, $111$, $117$, $119$, $123$, $125$, $127$, $171$, $175$, $183$, $187$, $191$, $219$, $223$, $239$, $255$, $511$ |
    | $10$ | $1023$ | $3$, $5$, $7$, $9$, $11$, $13$, $15$, $17$, $19$, $21$, $23$, $25$, $27$, $29$, $31$, $33$, $35$, $37$, $39$, $41$, $43$, $45$, $47$, $49$, $51$, $53$, $55$, $57$, $59$, $61$, $63$, $69$, $71$, $73$, $75$, $77$, $79$, $83$, $85$, $87$, $89$, $91$, $93$, $95$, $99$, $101$, $103$, $105$, $107$, $109$, $111$, $115$, $117$, $119$, $121$, $123$, $125$, $127$, $147$, $149$, $151$, $155$, $157$, $159$, $165$, $167$, $171$, $173$, $175$, $179$, $181$, $183$, $187$, $189$, $191$, $205$, $207$, $213$, $215$, $219$, $221$, $223$, $231$, $235$, $237$, $239$, $245$, $247$, $251$, $253$, $255$, $341$, $343$, $347$, $351$, $363$, $367$, $375$, $379$, $383$, $439$, $447$, $479$, $495$, $511$, $1023$ |

    Notes:
        - For $\delta = 3$ it reduces to the [Hamming code](/ref/HammingCode).
        - For $\delta = 2^{\mu} - 1$ it reduces to the [repetition code](/ref/RepetitionCode).

    Attributes:
        mu (int): The parameter $\mu$ of the BCH code.
        delta (int): The Bose distance $\delta$ of the BCH code.

    Examples:
        >>> code = komm.BCHCode(mu=5, delta=7)
        >>> (code.length, code.dimension, code.minimum_distance)
        (31, 16, np.int64(7))
        >>> code.generator_polynomial
        BinaryPolynomial(0b1000111110101111)

        >>> komm.BCHCode(mu=7, delta=31)
        BCHCode(mu=7, delta=31)

        >>> komm.BCHCode(mu=7, delta=32)
        Traceback (most recent call last):
        ...
        ValueError: 'delta' must be a Bose distance (the next one is 43)

        >>> komm.BCHCode(mu=7, delta=43)
        BCHCode(mu=7, delta=43)
    """

    mu: int
    delta: int

    def __attrs_post_init__(self) -> None:
        if self.mu < 2:
            raise ValueError("'mu' must satisfy mu >= 2")
        if not 2 <= self.delta <= 2**self.mu - 1:
            raise ValueError("'delta' must satisfy 2 <= delta <= 2**mu - 1")
        if self.phi(self.delta) in self.lcm_set:
            bose_distance = self.delta
            while self.phi(bose_distance) in self.lcm_set:
                bose_distance += 1
            raise ValueError(
                f"'delta' must be a Bose distance (the next one is {bose_distance})"
            )

    @cached_property
    def length(self) -> int:
        return 2**self.mu - 1

    @cached_property
    def generator_polynomial(self) -> BinaryPolynomial:
        return reduce(operator.mul, self.lcm_set)

    @property
    def default_decoder(self):
        return "berlekamp"

    @classmethod
    def supported_decoders(cls) -> list[str]:
        return cls.__base__.supported_decoders() + ["berlekamp"]  # type: ignore

    @cached_property
    def field(self):
        return FiniteBifield(self.mu)

    @cached_property
    def lcm_set(self) -> set[BinaryPolynomial]:
        return {self.phi(i) for i in range(1, self.delta)}

    @cache
    def phi(self, i: int) -> BinaryPolynomial:
        alpha = self.field.primitive_element
        return (alpha**i).minimal_polynomial()
