import pytest
from dupkeys import check, main


def test_json_dup():
    assert len(check("a.json", '{"a":1,"b":{"x":1,"x":2},"a":3}')) == 2

def test_json_clean():
    assert check("a.json", '{"a":1,"b":[{"a":1},{"a":2}]}') == []

def test_env_dup():
    r = check(".env", "A=1\n# c\nexport B=2\nA=3\n")
    assert r == [(4, "duplicate key 'A' (first at line 1; last value wins)")]

def test_ini_sections():
    t = "[a]\nx=1\n[b]\nx=2\n[a]\nx=3\n"
    assert [n for n, _ in check("c.ini", t)] == [6]

def test_properties_colon():
    assert len(check("x.properties", "a: 1\na=2\n")) == 1

def test_cli_codes(tmp_path, capsys):
    f = tmp_path / "a.json"; f.write_text('{"a":1,"a":2}')
    assert main([str(f)]) == 1
    f.write_text('{"a":1}')
    assert main([str(f)]) == 0
    f.write_text('{bad')
    assert main([str(f)]) == 2
    assert main([str(tmp_path / "nope")]) == 2
    assert "error" in capsys.readouterr().err

def test_force_type(tmp_path):
    f = tmp_path / "conf"; f.write_text("a=1\na=2\n")
    assert main(["--type", "env", str(f)]) == 1
