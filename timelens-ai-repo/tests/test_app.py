from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")

WRAP = '''
import io, streamlit as st
from PIL import Image
buf = io.BytesIO(); Image.new("RGB", (300, 200), (150, 120, 60)).save(buf, "PNG")
class F:
    def getvalue(self): return buf.getvalue()
st.file_uploader = lambda *a, **k: F() if k.get("key") != "museum_up" else None
exec(open(r"__APP__").read())
'''


def test_no_image_state():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert any("Upload an image" in i.value for i in at.info)


def test_full_demo_flow():
    at = AppTest.from_string(WRAP.replace('__APP__', APP), default_timeout=60).run()
    assert not at.exception, at.exception
    assert any("DEMO MODE" in w.value for w in at.warning)
    assert any("Nataraja" in s.value for s in at.subheader)
    assert len(at.tabs) == 10
    # save to museum
    [b for b in at.button if "Save to Virtual Museum" in b.label][0].click().run()
    assert not at.exception and len(at.session_state["museum"]) == 1
    # region question in demo mode
    [b for b in at.button if "Ask about this region" in b.label][0].click().run()
    assert not at.exception and "Demo mode" in at.session_state["region_answer"]
    # chat
    at.chat_input[0].set_value("Who built it?").run()
    assert not at.exception and len(at.session_state["chat"]) == 2
