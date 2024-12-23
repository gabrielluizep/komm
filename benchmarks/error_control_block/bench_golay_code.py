import numpy as np

import komm


def bench_decode_golay_matrix_exhaustive_search_hard(benchmark):
    code = komm.GolayCode()
    decoder = komm.BlockDecoder(code, method="exhaustive-search-hard")
    n_blocks = 1000
    r = np.random.randint(0, 2, size=n_blocks * code.length)
    benchmark(decoder, r)


def bench_decode_golay_matrix_syndrome_table(benchmark):
    code = komm.GolayCode()
    decoder = komm.BlockDecoder(code, method="syndrome-table")
    n_blocks = 1000
    r = np.random.randint(0, 2, size=n_blocks * code.length)
    benchmark(decoder, r)


def bench_decode_golay_polynomial_exhaustive_search_hard(benchmark):
    code = komm.CyclicCode(
        length=23, generator_polynomial=0b101011100011, systematic=False
    )
    decoder = komm.BlockDecoder(code, method="exhaustive-search-hard")
    n_blocks = 1000
    r = np.random.randint(0, 2, size=n_blocks * code.length)
    benchmark(decoder, r)


def bench_decode_golay_polynomial_syndrome_table(benchmark):
    code = komm.CyclicCode(
        length=23, generator_polynomial=0b101011100011, systematic=False
    )
    decoder = komm.BlockDecoder(code, method="syndrome-table")
    n_blocks = 1000
    r = np.random.randint(0, 2, size=n_blocks * code.length)
    benchmark(decoder, r)


def bench_decode_golay_polynomial_meggitt_table(benchmark):
    code = komm.CyclicCode(
        length=23, generator_polynomial=0b101011100011, systematic=True
    )
    decoder = komm.BlockDecoder(code, method="meggitt")
    n_blocks = 1000
    r = np.random.randint(0, 2, size=n_blocks * code.length)
    benchmark(decoder, r)
