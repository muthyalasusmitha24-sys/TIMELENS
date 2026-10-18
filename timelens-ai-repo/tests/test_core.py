import json
from PIL import Image
from timelens import demo, llm, visuals
from timelens.schema import extract_json, normalize, fmt_year


def test_normalize_garbage():
    for bad in (None, 5, "x", [], {"timeline": "no", "graph": 3, "confidence": "abc"}):
        d = normalize(bad)
        assert d["name"] and d["graph"]["nodes"] == []


def test_confidence_percent():
    assert normalize({"confidence": 85})["confidence"] == 0.85


def test_extract_json_fenced():
    assert extract_json('Sure:\n```json\n{"a": 1}\n```')["a"] == 1
    assert extract_json('text {"a": 2} tail')["a"] == 2


def test_graph_drops_dangling_edges():
    g = normalize({"graph": {"nodes": [{"id": "A"}], "edges": [{"source": "A", "target": "Z"}]}})["graph"]
    assert g["edges"] == []


def test_demo_visuals_render():
    a = normalize(demo.DEMO_ANALYSIS)
    for fn in (visuals.timeline_fig, visuals.map_fig, visuals.graph_fig):
        fig = fn(a)
        assert fig is not None
        fig.to_json()


def test_visuals_empty():
    a = normalize(None)
    assert visuals.timeline_fig(a) is None and visuals.map_fig(a) is None and visuals.graph_fig(a) is None


def test_analyze_demo_no_key():
    a, err = llm.analyze(Image.new("RGB", (50, 50)), "", "Explorer")
    assert err is None and a["name"].startswith("Chola")


def test_analyze_bad_key_does_not_crash():
    a, err = llm.analyze(Image.new("RGB", (50, 50)), "sk-ant-invalid", "Explorer")
    assert a["name"] == "Unidentified object" and err


def test_fmt_year():
    assert fmt_year(-500) == "500 BCE" and fmt_year(900) == "900 CE" and fmt_year(None) == "?"
