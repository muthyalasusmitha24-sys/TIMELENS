"""Similar-artifact discovery from open museum APIs (no key needed)."""
import requests

HEAD = {"User-Agent": "TimeLensAI/1.0 (educational)"}


def _get(url, params=None):
    try:
        r = requests.get(url, params=params, headers=HEAD, timeout=12)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def search_met(term, limit=4):
    data = _get("https://collectionapi.metmuseum.org/public/collection/v1/search",
                {"q": term, "hasImages": "true"})
    out = []
    for oid in (data or {}).get("objectIDs", [])[: limit * 2]:
        o = _get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}")
        if o and o.get("primaryImageSmall"):
            out.append({"museum": "The Met", "title": o.get("title", ""), "date": o.get("objectDate", ""),
                        "culture": o.get("culture", ""), "image": o["primaryImageSmall"],
                        "url": o.get("objectURL", "")})
        if len(out) >= limit:
            break
    return out


def search_artic(term, limit=4):
    data = _get("https://api.artic.edu/api/v1/artworks/search",
                {"q": term, "limit": limit, "fields": "id,title,date_display,image_id,place_of_origin"})
    out = []
    for o in (data or {}).get("data", []):
        if o.get("image_id"):
            out.append({"museum": "Art Institute of Chicago", "title": o.get("title", ""),
                        "date": o.get("date_display", ""), "culture": o.get("place_of_origin", ""),
                        "image": f"https://www.artic.edu/iiif/2/{o['image_id']}/full/400,/0/default.jpg",
                        "url": f"https://www.artic.edu/artworks/{o['id']}"})
    return out


def find_similar(terms, per_source=3):
    results, seen = [], set()
    for t in terms[:3]:
        for fn in (search_met, search_artic):
            for r in fn(t, per_source):
                if r["url"] not in seen:
                    seen.add(r["url"])
                    results.append(r)
    return results
