import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from bijlage import subcategorie_dict
from bijlage import kolom_aliases
import seaborn as sns
from check import check_data
from Kwadrant_1_aantallen import kwadrant1
from Kwadrant2_workload import kwadrant2
from Kwadrant3_tevredenheid import kwadrant3
from Kwadrant_4_termijn import kwadrant4
from export_pdf import maak_pdf

st.set_page_config(layout="wide")

st.markdown("""
    <style>
        html, body, [data-testid="stApp"] {
            background-color: black;
            color: white;
        }
        label {
            color: white !important;
        }
        .stSelectbox > div > div {
            background-color: black;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Meldingen Dashboard")

st.markdown("<h3 style ='text-align: left; color: #2E8B57;'>Upload hier een CSV-bestand...</h3>",
            unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload een CSV-bestand", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        resultaat, boodschap, df_schoon = check_data(df)
        if resultaat == "ok":
            st.success(boodschap)
            st.session_state["data"] = df_schoon
            st.session_state["data_ok"] = True
        elif resultaat == "warning":
            st.warning(boodschap)
        else:
            st.error(boodschap)
    except Exception as e:
        st.error(f"Fout bij het inlezen van bestand: {e}")

if st.session_state.get("data_ok", False):
    if st.session_state.get("data_ok", False):
        df = st.session_state["data"].copy()
        df["datum"] = pd.to_datetime(df["datum"], errors='coerce')
        df = df.dropna(subset=["datum"])
        st.subheader("📊 Overzicht: Aantallen en Workload per team")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Aantallen",
            "👷 Workload per team",
            "😊 Tevredenheid",
            "⏱️ Termijnanalyse",
            "📄 PDF-export"
        ])

        st.markdown("""
            <style>
            /* Tekstkleur van tabtitels wit maken */
            button[data-baseweb="tab"] {
                color: white !important;
            }

            /* Actieve tab wit + vet */
            button[data-baseweb="tab"][aria-selected="true"] {
                color: white !important;
                font-weight: bold;
                border-bottom: 2px solid white;
            }
            </style>
        """, unsafe_allow_html=True)

        with tab1:
            kwadrant1(df)

        with tab2:
            kwadrant2(df)

        with tab3:
            kwadrant3(df)

        with tab4:
            kwadrant4(df)

        with tab5:
            maak_pdf()







