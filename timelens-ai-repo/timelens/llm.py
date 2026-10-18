"""Claude vision + chat layer with automatic demo fallback."""
import base64
import io
import json
import os

from PIL import Image

from . import demo
from .schema import extract_json, normalize

MODEL = os.environ.get("TIMELENS_MODEL", "claude-sonnet-5-5")

MODES = {
    "Explorer": "Explain for a curious general audience; clear, vivid, accessible.",
    "Student": "Explain for a school/college student; define terms, add key takeaways.",
    "Archaeologist": ("Professional register: typology, fabric/material analysis, dating methodology, "
                      "comparanda, stratigraphic and provenance considerations, and scholarly caveats."),
    "Story": ("Write the narrative in the first person, as the artifact itself telling its own story, "
              "while keeping every factual claim accurate."),
}

ANALYSIS_PROMPT = """You are TimeLens AI, an expert historian, art historian and archaeologist.
Analyse the attached image of a historical object/site. Reply with ONE JSON object only (no prose, no fences) with keys:
identified(bool), name, category (sculpture|monument|temple|coin|inscription|manuscript|artifact|building|site|other),
confidence (0-1), period{label,start_year,end_year} (negative = BCE), civilization, origin{place,country,lat,lon},
material, style, significance, narrative (3-5 paragraphs), evidence (list of concrete VISIBLE features supporting your
identification), inscription{present,script,transcription,translation,notes}, timeline (6-10 items
{year,event,kind in dynasty|architecture|trade|religion|war|object}), map_points (3-6 {name,lat,lon,role}),
graph{nodes[{id,group}],edges[{source,target,label}]} (6-12 nodes: dynasties, religions, trade routes, styles, events),
connections (list of strings), search_terms (3-5 museum search keywords), uncertainties (list).
Rules: be honest. If the image is not a historical object, set identified=false and explain in narrative.
Never invent inscriptions: if text is unreadable say so. Give lower confidence when evidence is weak.
Mode instruction: {mode}"""


def get_client(api_key):
    import anthropic
    return anthropic.Anthropic(api_key=api_key, timeout=120.0, max_retries=2)


def prep_image(img: Image.Image, max_side=1568):
    img = img.convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return base64.standard_b64encode(buf.getvalue()).decode()


def _image_block(img):
    return {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": prep_image(img)}}


def _text(resp):
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")


def analyze(img, api_key, mode="Explorer"):
    """Returns (analysis_dict, error_or_None). Falls back to demo data when no key."""
    if not api_key:
        return normalize(demo.DEMO_ANALYSIS), None
    try:
        client = get_client(api_key)
        resp = client.messages.create(
            model=MODEL, max_tokens=4096,
            messages=[{"role": "user", "content": [
                _image_block(img),
                {"type": "text", "text": ANALYSIS_PROMPT.replace("{mode}", MODES.get(mode, MODES["Explorer"]))}]}])
        return normalize(extract_json(_text(resp))), None
    except Exception as e:  # surfaced in the UI, never crashes the app
        return normalize(None), f"{type(e).__name__}: {e}"


def ask_region(img_crop, analysis, question, api_key, mode="Explorer"):
    if not api_key:
        return demo.DEMO_CHAT
    try:
        client = get_client(api_key)
        ctx = json.dumps({k: analysis[k] for k in ("name", "period", "civilization", "origin", "material", "style")})
        resp = client.messages.create(
            model=MODEL, max_tokens=900,
            messages=[{"role": "user", "content": [
                _image_block(img_crop),
                {"type": "text", "text": f"This crop is a selected region of an object. Context: {ctx}\n"
                                         f"Mode: {MODES.get(mode)}\nQuestion about this region: {question}\n"
                                         "Explain what this part is and its meaning. Be honest about uncertainty."}]}])
        return _text(resp)
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


def chat(history, analysis, api_key, mode="Explorer"):
    """history: list of {role, content}. Returns reply string."""
    if not api_key:
        return demo.DEMO_CHAT
    try:
        client = get_client(api_key)
        system = ("You are the TimeLens AI Historian. Answer using the analysis below and your knowledge. "
                  "Separate established fact from interpretation; admit uncertainty. "
                  f"Mode: {MODES.get(mode)}\nANALYSIS:\n{json.dumps(analysis)[:6000]}")
        resp = client.messages.create(model=MODEL, max_tokens=1000, system=system,
                                      messages=history[-12:])
        return _text(resp)
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"
