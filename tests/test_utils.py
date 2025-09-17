from lib.utils import wrap_index, int_or_none, boolish

def test_wrap_index():
    assert wrap_index(0, 5) == 0
    assert wrap_index(5, 5) == 0
    assert wrap_index(6, 5) == 1

def test_int_or_none():
    assert int_or_none("10") == 10
    assert int_or_none("x") is None

def test_boolish():
    assert boolish("1")
    assert boolish("True")
    assert boolish("sim")
    assert not boolish("0")
