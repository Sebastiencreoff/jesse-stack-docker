#! /usr/bin/env python
import numpy as np

import jesse.indicators as ta


def kdj(
    candles: np.ndarray,
    fastk_period: int = 9,
    slowk_matype: int = 0,
    slowk_period: int = 3,
    slowd_period: int = 3,
) -> np.ndarray:
    """
        fastk_period = 9
        lowk_matype = 0,
        slowk_period = 3,
        slowd_period = 3

    return: K, D, J
    """

    # candles example array([1.6172352e+12, open, close, high,low, 5.6541492e+01])
    K, D = ta.stoch(
        candles,
        fastk_period=fastk_period,
        slowk_matype=slowk_matype,
        slowk_period=slowk_period,
        slowd_period=slowd_period,
    )

    return K, D, 3 * K - 2 * D
