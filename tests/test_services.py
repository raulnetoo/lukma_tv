from lib.services import load_units_from_config

def test_units_default():
    u = load_units_from_config()
    assert len(u) == 4
    assert any("São José do Rio Preto" in x["city"] for x in u)
