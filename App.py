import streamlit as st
import json
import io
import traceback
from datetime import datetime

# Optional: import joltpy if installed
try:
    from joltpy import Chainr
    JOLT_AVAILABLE = True
except ImportError:
    JOLT_AVAILABLE = False

# --- Page setup ---
st.set_page_config(page_title="JOLT Transformer Demo", layout="wide")

# --- Custom refined dark theme ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Oswald&display=swap" rel="stylesheet">
    <style>
        body {
            background-color: #0b0b0b;
            color: #eaeaea;
        }
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
        .stTextArea textarea {
            background-color: #1c1c1c !important;
            color: #eaeaea !important;
            border-radius: 8px;
            font-size: 15px;
        }
        .stFileUploader {
            color: #eaeaea;
        }
        .css-1kyxreq {
            background-color: #141414 !important;
        }
        .stButton button {
            background-color: #e63946 !important;
            color: white !important;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .stButton button:hover {
            background-color: #c32f3b !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title and intro ---
st.title("JOLT Transformer Demo")
st.caption("Lightweight prototype for visualizing JSON-to-JSON transformations using JOLT specifications.")

# --- Sidebar ---
st.sidebar.header("About this Demo")
st.sidebar.info("""
This Streamlit prototype emulates the transformation logic that the full XYPRO JOLT
backend will provide. It allows testing with local or uploaded JSONs for both
the source data and the JOLT specification.
""")

# --- Example data loader ---
def load_example_data():
    source_example = {
        "user": {
            "firstName": "Alice",
            "lastName": "Smith",
            "location": {"city": "Los Angeles", "state": "CA"}
        }
    }
    spec_example = [
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
    return json.dumps(source_example, indent=2), json.dumps(spec_example, indent=2)

# --- Columns for source/spec ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Source JSON")
    src_file = st.file_uploader("Upload a Source JSON file", type=["json"], key="src")
    src_text = st.text_area("Or paste Source JSON here", height=260, placeholder='{\n  "name": "John", "age": 30\n}')
    if src_file:
        src_text = src_file.read().decode("utf-8")

with col2:
    st.subheader("JOLT Spec JSON")
    spec_file = st.file_uploader("Upload a JOLT Spec file", type=["json"], key="spec")
    spec_text = st.text_area("Or paste JOLT Spec here", height=260, placeholder='[{"operation": "shift", "spec": {"name": "person.name"}}]')
    if spec_file:
        spec_text = spec_file.read().decode("utf-8")

# --- Load example button ---
if st.button("Load Example Data"):
    src_text, spec_text = load_example_data()
    st.session_state["src_text"] = src_text
    st.session_state["spec_text"] = spec_text
    st.rerun()

# --- Run transformation button ---
st.markdown("---")

if st.button("Run Transformation"):
    try:
        source = json.loads(src_text)
        spec = json.loads(spec_text)

        if JOLT_AVAILABLE:
            chainr = Chainr(spec)
            result = chainr.transform(source)
        else:
            result = {"simulatedResult": {"originalKeys": list(source.keys()), "transformed": True}}

        st.success("Transformation executed successfully")
        st.json(result)

        # Download button
        download_bytes = io.BytesIO(json.dumps(result, indent=2).encode("utf-8"))
        st.download_button(
            label="Download Result JSON",
            data=download_bytes,
            file_name=f"jolt_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

        # Record transformation in history
        if "history" not in st.session_state:
            st.session_state["history"] = []
        st.session_state["history"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "source_keys": ", ".join(source.keys()),
        })

    except json.JSONDecodeError:
        st.error("Invalid JSON detected. Please verify your syntax.")
        st.code(traceback.format_exc())
    except Exception as e:
        st.error("Transformation failed.")
        st.code(traceback.format_exc())

# --- Expanders for previews and logs ---
st.markdown("---")

with st.expander("Preview Inputs"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Source JSON Preview:**")
        try:
            st.json(json.loads(src_text or "{}"))
        except Exception:
            st.warning("Invalid or empty source JSON.")
    with c2:
        st.markdown("**JOLT Spec Preview:**")
        try:
            st.json(json.loads(spec_text or "{}"))
        except Exception:
            st.warning("Invalid or empty spec JSON.")

with st.expander("Transformation History"):
    if "history" in st.session_state and st.session_state["history"]:
        st.table(st.session_state["history"])
    else:
        st.info("No transformations recorded yet.")
