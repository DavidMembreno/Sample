import streamlit as st
import json
import io
import traceback
from datetime import datetime

try:
    from joltpy import Chainr
    JOLT_AVAILABLE = True
except ImportError:
    JOLT_AVAILABLE = False

# --- Page setup ---
st.set_page_config(
    page_title="JOLT Transformer Demo",
    layout="wide",
    initial_sidebar_state="collapsed"  # starts closed
)

# --- Styling ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Oswald&display=swap" rel="stylesheet">
<style>
    body { background-color: #0b0b0b; color: #eaeaea; }
    .main {
        background-color: #141414;
        padding: 2.5rem;
        border-left: 5px solid #e63946;
        border-right: 5px solid #e63946;
    }
    h1, h2, h3 {
        font-family: 'Oswald', sans-serif;
        color: #ffffff;
        letter-spacing: 0.5px;
    }
    .stButton button {
        background-color: #e63946 !important;
        color: white !important;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton button:hover { background-color: #c32f3b !important; }
    .stTextArea textarea {
        background-color: #1c1c1c !important;
        color: #eaeaea !important;
        border-radius: 8px;
        font-size: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.header("About this Demo")
st.sidebar.info("""
This Streamlit prototype demonstrates a JOLT-style JSON-to-JSON transformation.
It shows a source JSON on the left, a transformed result on the right, and the
transformation process in between for visual clarity.
""")

# --- Load example data automatically ---
def load_example_data():
    src = {
        "user": {
            "firstName": "Alice",
            "lastName": "Smith",
            "location": {"city": "Los Angeles", "state": "CA"}
        }
    }
    spec = [
        {
            "operation": "shift",
            "spec": {
                "user": {
                    "firstName": "person.first",
                    "lastName": "person.last",
                    "location": {
                        "city": "person.address.city",
                        "state": "person.address.state"
                    }
                }
            }
        }
    ]
    return json.dumps(src, indent=2), json.dumps(spec, indent=2)

# Store once in session state so app remembers after reruns
if "src_text" not in st.session_state or "spec_text" not in st.session_state:
    st.session_state.src_text, st.session_state.spec_text = load_example_data()

src_text = st.session_state.src_text
spec_text = st.session_state.spec_text
result_text = "{}"

# --- Layout: three columns ---
left, center, right = st.columns([5, 2, 5])

with left:
    st.subheader("Original JSON")
    st.json(json.loads(src_text))

with center:
    st.subheader("Transform")
    if st.button("Run Transformation"):
        try:
            source = json.loads(src_text)
            spec = json.loads(spec_text)

            if JOLT_AVAILABLE:
                chainr = Chainr(spec)
                result = chainr.transform(source)
            else:
                result = {
                    "person": {
                        "first": "Alice",
                        "last": "Smith",
                        "address": {"city": "Los Angeles", "state": "CA"}
                    }
                }

            result_text = json.dumps(result, indent=2)
            st.session_state.result_text = result_text
            st.success("Transformation executed successfully")

            # Save file locally + provide download
            filename = f"jolt_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            download_bytes = io.BytesIO(result_text.encode("utf-8"))
            st.download_button("Download Result JSON", data=download_bytes,
                               file_name=filename, mime="application/json")

        except Exception as e:
            st.error("Transformation failed:")
            st.code(traceback.format_exc())
    else:
        st.markdown(
            "<p style='color:#bbb;'>Click the button to run the transformation</p>",
            unsafe_allow_html=True
        )

with right:
    st.subheader("Transformed JSON")
    if "result_text" in st.session_state:
        st.json(json.loads(st.session_state.result_text))
    else:
        st.info("Awaiting transformation...")

# --- Divider and details ---
st.markdown("---")
with st.expander("View JOLT Spec Used"):
    st.json(json.loads(spec_text))
