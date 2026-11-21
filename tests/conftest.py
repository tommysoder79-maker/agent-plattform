import copy
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROT / "scripts"))

from validera_kontrakt import las_yaml  # noqa: E402

EXEMPEL = ROT / "schema" / "exempel"


@pytest.fixture
def las():
    """Läsdelen av Yahoo-exemplet: giltig, nivå 2 (A + B)."""
    return copy.deepcopy(las_yaml(EXEMPEL / "yahoo-rensning-las.yaml"))


@pytest.fixture
def utfor():
    """Utförardelen av Yahoo-exemplet: giltig, nivå 2 (B + C)."""
    return copy.deepcopy(las_yaml(EXEMPEL / "yahoo-rensning-utfor.yaml"))
