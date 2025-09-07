import pytest

from ppqm import chembridge

# from context import ppqm, molcalc
#
# from molcalc.ppqm import chembridge


TEST_ERROR_SMILES = ["C[NH4+]"]


@pytest.mark.parametrize("smiles", TEST_ERROR_SMILES)
def test_capture_error(smiles):

    molobj = chembridge.smiles_to_molobj(smiles)

    assert molobj is None

    return
