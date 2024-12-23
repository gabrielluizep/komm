from abc import ABC, abstractmethod
from functools import cached_property

import numpy as np
import numpy.typing as npt
from attrs import frozen
from numpy.linalg import matrix_power

from .._error_control_block import BlockCode
from .._types import ArrayIntLike
from .._util.bit_operations import binlist2int, int2binlist, pack
from .._util.matrices import pseudo_inverse
from .ConvolutionalCode import ConvolutionalCode


@frozen
class TerminationStrategy(ABC):
    convolutional_code: "ConvolutionalCode"
    num_blocks: int

    @abstractmethod
    def initial_state(self, input_bits: ArrayIntLike) -> int: ...

    @abstractmethod
    def pre_process_input(self, input_bits: ArrayIntLike) -> npt.NDArray[np.int_]: ...

    @abstractmethod
    def codeword_length(self) -> int: ...

    @abstractmethod
    def generator_matrix(self, code: BlockCode) -> npt.NDArray[np.int_]: ...


def _base_generator_matrix(
    code: BlockCode, convolutional_code: ConvolutionalCode, num_blocks: int
) -> npt.NDArray[np.int_]:
    k0 = convolutional_code.num_input_bits
    n0 = convolutional_code.num_output_bits
    k, n = code.dimension, code.length
    generator_matrix = np.zeros((k, n), dtype=int)
    top_rows = np.apply_along_axis(code.enc_mapping, 1, np.eye(k0, k, dtype=int))
    for t in range(num_blocks):
        generator_matrix[k0 * t : k0 * (t + 1), :] = np.roll(top_rows, n0 * t, 1)
    return generator_matrix


@frozen
class DirectTruncation(TerminationStrategy):
    def initial_state(self, input_bits: ArrayIntLike) -> int:
        return 0

    def pre_process_input(self, input_bits: ArrayIntLike) -> npt.NDArray[np.int_]:
        n = self.convolutional_code.num_input_bits
        return pack(input_bits, width=n)

    def codeword_length(self) -> int:
        h = self.num_blocks
        n = self.convolutional_code.num_output_bits
        return h * n

    def generator_matrix(self, code: BlockCode) -> npt.NDArray[np.int_]:
        h = self.num_blocks
        k0 = self.convolutional_code.num_input_bits
        n0 = self.convolutional_code.num_output_bits
        generator_matrix = _base_generator_matrix(code, self.convolutional_code, h)
        for t in range(1, h):
            generator_matrix[k0 * t : k0 * (t + 1), : n0 * t] = 0
        return generator_matrix


@frozen
class ZeroTermination(TerminationStrategy):
    def initial_state(self, input_bits: npt.ArrayLike) -> int:
        return 0

    def pre_process_input(self, input_bits: ArrayIntLike) -> npt.NDArray[np.int_]:
        n = self.convolutional_code.num_input_bits
        tail = input_bits @ self._tail_projector % 2
        return pack(np.concatenate([input_bits, tail]), width=n)

    def codeword_length(self) -> int:
        h = self.num_blocks
        n = self.convolutional_code.num_output_bits
        m = self.convolutional_code.memory_order
        return (h + m) * n

    def generator_matrix(self, code: BlockCode) -> npt.NDArray[np.int_]:
        return _base_generator_matrix(code, self.convolutional_code, self.num_blocks)

    @cached_property
    def _tail_projector(self) -> npt.NDArray[np.int_]:
        h = self.num_blocks
        mu = self.convolutional_code.memory_order
        A_mat, B_mat, _, _ = self.convolutional_code.state_space_representation()
        AnB_message = np.vstack(
            [B_mat @ matrix_power(A_mat, j) % 2 for j in range(mu + h - 1, mu - 1, -1)]
        )
        AnB_tail = np.vstack(
            [B_mat @ matrix_power(A_mat, j) % 2 for j in range(mu - 1, -1, -1)]
        )
        return AnB_message @ pseudo_inverse(AnB_tail) % 2


@frozen
class TailBiting(TerminationStrategy):
    def initial_state(self, input_bits: ArrayIntLike) -> int:
        fsm = self.convolutional_code.finite_state_machine()
        nu = self.convolutional_code.overall_constraint_length
        _, zs_response = fsm.process(input_bits, initial_state=0)
        zs_response = int2binlist(zs_response, width=nu)
        return binlist2int(zs_response @ self._zs_multiplier % 2)

    def pre_process_input(self, input_bits: ArrayIntLike) -> npt.NDArray[np.int_]:
        n = self.convolutional_code.num_input_bits
        return pack(input_bits, width=n)

    def codeword_length(self) -> int:
        h = self.num_blocks
        n = self.convolutional_code.num_output_bits
        return h * n

    def generator_matrix(self, code: BlockCode) -> npt.NDArray[np.int_]:
        return _base_generator_matrix(code, self.convolutional_code, self.num_blocks)

    @cached_property
    def _zs_multiplier(self) -> npt.NDArray[np.int_]:
        h = self.num_blocks
        nu = self.convolutional_code.overall_constraint_length
        A_mat, _, _, _ = self.convolutional_code.state_space_representation()
        return pseudo_inverse(matrix_power(A_mat, h) + np.eye(nu, dtype=int) % 2)
