"""Analysis schema + safe parsing so the UI never crashes on odd model output."""
import json
import re

DEFAULT = {
    "identified": False,
    "name": "Unidentified object",
    "category": "unknown",
    "confidence": 0.0,
    "period": {"label": "Unknown", "start_year": None, "end_year": None},
    "civilization": "Unknown",
    "origin": {"place": "Unknown", "country": "", "lat": None, "lon": None},
    "material": "Unknown",
    "style": "Unknown",
    "significance": "",
    "narrative": "",
    "evidence": [],
    "inscription": {"present": False, "script": "", "transcription": "", "translation": "", "notes": ""},
    "timeline": [],
    "map_points": [],
    "graph": {"nodes": [], "edges": []},
    "connections": [],
    "search_terms": [],
    "uncertainties": [],
}


def _num(v):
    try:
        if v is None or v == "":
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def extract_json(text):
    """Pull the first JSON object out of a model reply (handles ``` fences)."""
    if not text:
        raise ValueError("empty reply")
    t = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", t, re.S)
    if fence:
        t = fence.group(1)
    start, end = t.find("{"), t.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in reply")
    return json.loads(t[start:end + 1])


def normalize(raw):
    """Merge a raw dict onto DEFAULT, coercing types. Never raises."""
    d = json.loads(json.dumps(DEFAULT))
    if not isinstance(raw, dict):
        return d
    for k in ("name", "category", "civilization", "material", "style", "significance", "narrative"):
        if isinstance(raw.get(k), str) and raw[k].strip():
            d[k] = raw[k].strip()
    d["identified"] = bool(raw.get("identified", True))
    c = _num(raw.get("confidence"))
    if c is not None:
        d["confidence"] = max(0.0, min(1.0, c / 100 if c > 1 else c))
    p = raw.get("period")
    if isinstance(p, dict):
        d["period"] = {"label": str(p.get("label") or "Unknown"),
                       "start_year": _num(p.get("start_year")), "end_year": _num(p.get("end_year"))}
    o = raw.get("origin")
    if isinstance(o, dict):
        d["origin"] = {"place": str(o.get("place") or "Unknown"), "country": str(o.get("country") or ""),
                       "lat": _num(o.get("lat")), "lon": _num(o.get("lon"))}
    ins = raw.get("inscription")
    if isinstance(ins, dict):
        d["inscription"] = {k: (ins.get(k) if k == "present" else str(ins.get(k) or ""))
                            for k in ("present", "script", "transcription", "translation", "notes")}
        d["inscription"]["present"] = bool(ins.get("present"))
    for k in ("evidence", "connections", "search_terms", "uncertainties"):
        v = raw.get(k)
        if isinstance(v, list):
            d[k] = [str(x) for x in v if x]
    tl = []
    for e in raw.get("timeline") or []:
        if isinstance(e, dict) and _num(e.get("year")) is not None:
            tl.append({"year": _num(e["year"]), "event": str(e.get("event") or ""),
                       "kind": str(e.get("kind") or "event")})
    d["timeline"] = sorted(tl, key=lambda x: x["year"])
    mp = []
    for e in raw.get("map_points") or []:
        if isinstance(e, dict) and _num(e.get("lat")) is not None and _num(e.get("lon")) is not None:
            mp.append({"name": str(e.get("name") or ""), "lat": _num(e["lat"]), "lon": _num(e["lon"]),
                       "role": str(e.get("role") or "")})
    d["map_points"] = mp
    g = raw.get("graph")
    if isinstance(g, dict):
        nodes = [{"id": str(n.get("id")), "group": str(n.get("group") or "other")}
                 for n in g.get("nodes") or [] if isinstance(n, dict) and n.get("id")]
        ids = {n["id"] for n in nodes}
        edges = [{"source": str(e.get("source")), "target": str(e.get("target")), "label": str(e.get("label") or "")}
                 for e in g.get("edges") or []
                 if isinstance(e, dict) and str(e.get("source")) in ids and str(e.get("target")) in ids]
        d["graph"] = {"nodes": nodes, "edges": edges}
    return d


def fmt_year(y):
    if y is None:
        return "?"
    y = int(round(y))
    return f"{abs(y)} BCE" if y < 0 else f"{y} CE"
