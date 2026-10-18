import base64
import hashlib
import io
import json
import os

import streamlit as st
from PIL import Image, ImageDraw

from timelens import llm, museums, visuals
from timelens.schema import fmt_year, normalize

st.set_page_config(page_title="TimeLens AI", page_icon="🏺", layout="wide")


def secret_key():
    try:
        return st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        return ""


@st.cache_data(show_spinner=False, ttl=3600)
def cached_similar(terms):
    return museums.find_similar(list(terms))


def thumb_b64(img, side=240):
    t = img.convert("RGB")
    t.thumbnail((side, side))
    b = io.BytesIO()
    t.save(b, format="JPEG", quality=80)
    return base64.b64encode(b.getvalue()).decode()


ss = st.session_state
ss.setdefault("analysis", None)
ss.setdefault("img_hash", None)
ss.setdefault("chat", [])
ss.setdefault("museum", [])
ss.setdefault("error", None)
ss.setdefault("region_answer", "")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("🏺 TimeLens AI")
    st.caption("Upload a historical object. Explore its place in human history.")
    key_in = st.text_input("Anthropic API key", type="password",
                           value="", help="Stored only in this browser session. Leave empty for demo mode.")
    api_key = key_in.strip() or secret_key() or os.environ.get("ANTHROPIC_API_KEY", "")
    st.success("Live AI mode") if api_key else st.info("Demo mode (sample data, no key)")
    mode = st.selectbox("Mode", list(llm.MODES), help="Changes tone and depth of explanations.")
    st.markdown("---")
    st.caption("AI can be wrong. Dates and attributions are estimates; verify with museum or scholarly sources.")

# ---------------- Input ----------------
st.header("TimeLens AI")
src = st.radio("Image source", ["Upload", "Live camera"], horizontal=True)
file = st.file_uploader("Upload a photo (jpg/png/webp)", type=["jpg", "jpeg", "png", "webp"]) \
    if src == "Upload" else st.camera_input("Point at a monument or artifact")

img = None
if file is not None:
    try:
        raw = file.getvalue()
        img = Image.open(io.BytesIO(raw))
        img.load()
        img = img.convert("RGB")
    except Exception:
        st.error("Could not read that image. Try a JPG or PNG.")
        img = None

if img is None:
    st.info("Upload an image or use the camera to begin. No key? You will see a clearly labelled demo analysis.")
    st.stop()

h = hashlib.md5(raw + mode.encode() + (b"k" if api_key else b"d")).hexdigest()
col_img, col_main = st.columns([1, 2])
with col_img:
    st.image(img, use_container_width=True)
    if st.button("🔍 Analyze", type="primary", use_container_width=True) or (ss.img_hash != h and ss.analysis is None):
        with st.spinner("Studying the object..."):
            a, err = llm.analyze(img, api_key, mode)
        ss.analysis, ss.img_hash, ss.error, ss.chat, ss.region_answer = a, h, err, [], ""

a = ss.analysis
if ss.error:
    st.error(f"Analysis failed: {ss.error}")
if a is None:
    st.stop()
if ss.img_hash != h:
    st.warning("Image or mode changed since the last analysis. Press Analyze to refresh.")
if not api_key:
    st.warning("DEMO MODE: the analysis below is built-in sample data, not about your image.")

with col_main:
    st.subheader(a["name"])
    c1, c2, c3 = st.columns(3)
    p = a["period"]
    c1.metric("Period", p["label"], f"{fmt_year(p['start_year'])} – {fmt_year(p['end_year'])}"
              if p["start_year"] is not None else None, delta_color="off")
    c2.metric("Civilization", a["civilization"])
    c3.metric("Confidence", f"{int(a['confidence'] * 100)}%")
    st.progress(a["confidence"])
    st.write(f"**Origin:** {a['origin']['place']} {a['origin']['country']}  \n"
             f"**Material:** {a['material']}  \n**Style:** {a['style']}  \n**Category:** {a['category']}")
    if st.button("💾 Save to Virtual Museum"):
        ss.museum.append({"analysis": a, "thumb": thumb_b64(img)})
        st.toast("Saved!")

tabs = st.tabs(["📖 Story", "🔬 Evidence", "📜 Script", "⏳ Timeline", "🗺️ Map", "🕸️ Connections",
                "🏛️ Similar", "🎯 Ask a region", "💬 Historian", "🖼️ My Museum"])

with tabs[0]:
    st.markdown(a["narrative"] or "_No narrative available._")
    if a["significance"]:
        st.info(a["significance"])
    for u in a["uncertainties"]:
        st.caption(f"⚠️ {u}")

with tabs[1]:
    st.markdown("**Why the model thinks so:**")
    for e in a["evidence"] or ["No specific evidence listed."]:
        st.markdown(f"- {e}")

with tabs[2]:
    ins = a["inscription"]
    if ins["present"]:
        st.markdown(f"**Script:** {ins['script'] or 'unknown'}")
        st.code(ins["transcription"] or "(not readable)")
        st.markdown(f"**Translation:** {ins['translation'] or '—'}")
        if ins["notes"]:
            st.caption(ins["notes"])
        st.caption("Ancient-script readings are uncertain. Confirm with an epigraphist.")
    else:
        st.info(ins["notes"] or "No inscription detected.")

with tabs[3]:
    f = visuals.timeline_fig(a)
    st.plotly_chart(f, use_container_width=True) if f else st.info("No timeline data.")

with tabs[4]:
    f = visuals.map_fig(a)
    st.plotly_chart(f, use_container_width=True) if f else st.info("No location data.")

with tabs[5]:
    f = visuals.graph_fig(a)
    st.plotly_chart(f, use_container_width=True) if f else st.info("No graph data.")
    for c in a["connections"]:
        st.markdown(f"- {c}")

with tabs[6]:
    terms = tuple(a["search_terms"]) or (a["name"],)
    if st.button("Search museum collections"):
        with st.spinner("Searching The Met and Art Institute of Chicago..."):
            ss["similar"] = cached_similar(terms)
    res = ss.get("similar")
    if res is not None and not res:
        st.info("No results (museum APIs may be unreachable).")
    for i in range(0, len(res or []), 3):
        cols = st.columns(3)
        for col, r in zip(cols, res[i:i + 3]):
            col.image(r["image"], use_container_width=True)
            col.markdown(f"**[{r['title'][:60]}]({r['url']})**  \n{r['museum']} · {r['date']}")

with tabs[7]:
    st.caption("Choose a region of the image (percent of width/height), then ask about it.")
    x0, x1 = st.slider("Horizontal %", 0, 100, (25, 75))
    y0, y1 = st.slider("Vertical %", 0, 100, (25, 75))
    W, H = img.size
    box = (int(W * x0 / 100), int(H * y0 / 100), int(W * x1 / 100), int(H * y1 / 100))
    if box[2] - box[0] < 10 or box[3] - box[1] < 10:
        st.warning("Region too small.")
    else:
        prev = img.copy()
        ImageDraw.Draw(prev).rectangle(box, outline="#ff3030", width=max(3, W // 200))
        cc1, cc2 = st.columns(2)
        cc1.image(prev, caption="Selected area", use_container_width=True)
        crop = img.crop(box)
        cc2.image(crop, caption="Crop", use_container_width=True)
        q = st.text_input("Your question", "What is this part and what does it mean?")
        if st.button("Ask about this region"):
            with st.spinner("Looking closely..."):
                ss.region_answer = llm.ask_region(crop, a, q, api_key, mode)
        if ss.region_answer:
            st.markdown(ss.region_answer)

with tabs[8]:
    for m in ss.chat:
        st.chat_message(m["role"]).markdown(m["content"])
    if q := st.chat_input("Ask the historian anything about this object..."):
        ss.chat.append({"role": "user", "content": q})
        with st.spinner("Thinking..."):
            reply = llm.chat(ss.chat, a, api_key, mode)
        ss.chat.append({"role": "assistant", "content": reply})
        st.rerun()

with tabs[9]:
    up = st.file_uploader("Load a saved museum (.json)", type=["json"], key="museum_up")
    if up is not None and st.button("Import"):
        try:
            data = json.loads(up.getvalue())
            ss.museum.extend({"analysis": normalize(d["analysis"]), "thumb": d.get("thumb", "")} for d in data)
            st.success(f"Imported {len(data)} items")
        except Exception:
            st.error("Not a valid museum file.")
    if not ss.museum:
        st.info("Nothing saved yet. Use 'Save to Virtual Museum' above.")
    else:
        st.download_button("Download my museum", json.dumps(ss.museum), "museum_timelens.json", "application/json")
        for i in range(0, len(ss.museum), 3):
            cols = st.columns(3)
            for j, (col, it) in enumerate(zip(cols, ss.museum[i:i + 3])):
                if it.get("thumb"):
                    col.image(base64.b64decode(it["thumb"]), use_container_width=True)
                col.markdown(f"**{it['analysis']['name']}**  \n{it['analysis']['period']['label']}")
                if col.button("Remove", key=f"rm{i + j}"):
                    ss.museum.pop(i + j)
                    st.rerun()
