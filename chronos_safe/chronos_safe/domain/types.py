"""Shared type aliases."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

ArrayF64 = NDArray[np.float64]
JsonDict = dict[str, Any]
