import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from bijlage import subcategorie_dict
import seaborn as sns

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


# Titel en introductie
st.title("Meldingen Dashboard")

st.markdown(
    """<h3 style ='text-align: center; color: #2E8B57;'>Upload hier een CSV-bestand met klachtenregistraties. 
    Het bestand wordt automatisch gecontroleerd op geldigheid en volledigheid.</h3>""",
    unsafe_allow_html=True)

# Bestand uploaden
uploaded_file = st.file_uploader("Upload een CSV-bestand", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()  # Kolomnamen opschonen

        # Vereiste kolommen
        vereiste_kolommen = [
            "indexnummer", "klachtnummer", "naam", "email", "telefoon", "datum",
            "hoofdcategorie", "subcategorie", "behandeltermijn", "status", "bron",
            "gebied", "wijk", "tevredenheid", "team", "wijziging"
        ]

        if not all(k in df.columns for k in vereiste_kolommen):
            st.error("Het CSV-bestand mist één of meer verplichte kolommen. Controleer het formaat.")
        else:
            totaal_rijen = df.shape[0]
            aantal_nan_rijen = df[df.isnull().any(axis=1)].shape[0]

            if aantal_nan_rijen / totaal_rijen < 0.5:
                st.error("Er zijn te veel ontbrekende waarden. Herzie het CSV-bestand.")
            else:
                df_schoon = df.dropna()
                aantal_verwijderd = totaal_rijen - df_schoon.shape[0]

                if aantal_verwijderd > 0:
                    st.warning(f"{aantal_verwijderd} rijen met ontbrekende waarden zijn verwijderd.")
                    if st.button("OK"):
                        st.session_state["data_ok"] = True
                        st.session_state["data"] = df_schoon
                else:
                    st.success("CSV is succesvol ingelezen zonder ontbrekende waarden.")
                    st.session_state["data_ok"] = True
                    st.session_state["data"] = df

    except Exception as e:
        st.error(f"Fout bij het inlezen van het bestand: {e}")

# ========= KWADRANT 1A: Aantallen (Lijngrafiek) =========
if st.session_state.get("data_ok", False):
    df = st.session_state["data"]
    st.header("📈 Klachtaantallen in de tijd")

    # Zorg dat datum bruikbaar is
    df["datum"] = pd.to_datetime(df["datum"], errors='coerce')
    df = df.dropna(subset=["datum"])

    # Filterkolommen
    col1, col2 = st.columns([1, 3])
    with col1:
        hoofdcategorie = st.selectbox("Filter op hoofdcategorie", ["Alles"] + sorted(df["hoofdcategorie"].dropna().unique()))

        if hoofdcategorie in subcategorie_dict:
            sub_opties = ["Alles"] + subcategorie_dict[hoofdcategorie]
        else:
            sub_opties = ["Alles"] + sorted(df["subcategorie"].dropna().unique())

        subcategorie = st.selectbox("Filter op subcategorie", sub_opties)

        team = st.selectbox("Filter op team", ["Alles"] + sorted(df["team"].dropna().unique()))
        wijk = st.selectbox("Filter op wijk", ["Alles"] + sorted(df["wijk"].dropna().unique()))
        gebied = st.selectbox("Filter op gebied", ["Alles"] + sorted(df["gebied"].dropna().unique()))
        bron = st.selectbox("Filter op bron", ["Alles"] + sorted(df["bron"].dropna().unique()))

    with col2:
        tijdseenheid = st.radio("Toon meldingen per:", ["maand", "week"], horizontal=True)

    # Pas filters toe
    df_filtered = df.copy()
    if hoofdcategorie != "Alles":
        df_filtered = df_filtered[df_filtered["hoofdcategorie"] == hoofdcategorie]
    if subcategorie != "Alles":
        df_filtered = df_filtered[df_filtered["subcategorie"] == subcategorie]
    if team != "Alles":
        df_filtered = df_filtered[df_filtered["team"] == team]
    if wijk != "Alles":
        df_filtered = df_filtered[df_filtered["wijk"] == wijk]
    if gebied != "Alles":
        df_filtered = df_filtered[df_filtered["gebied"] == gebied]
    if bron != "Alles":
        df_filtered = df_filtered[df_filtered["bron"] == bron]

    # Groeperen op tijdseenheid
    if tijdseenheid == "maand":
        df_filtered["tijd"] = df_filtered["datum"].dt.to_period("M").astype(str)
        xlabel = "Maand"
    else:
        df_filtered["tijd"] = df_filtered["datum"].dt.to_period("W").astype(str)
        xlabel = "Week"

    tijdlijn = df_filtered["tijd"].value_counts().sort_index()

    # Plotten
    if tijdlijn.empty:
        st.info("Geen meldingen gevonden voor deze combinatie van filters.")
    else:
        fig, ax = plt.subplots()
        fig.patch.set_facecolor('black')
        ax.plot(tijdlijn.index, tijdlijn.values, marker='o', linestyle='-', color='blue')
        ax.set_title(f"Aantal klachten per {tijdseenheid}")
        ax.tick_params(axis='x', colors='white')  # voor x-as labels
        ax.tick_params(axis='y', colors='white')  # voor y-as labels
        ax.set_facecolor('black')
        ax.set_xlabel(xlabel, color='white')
        ax.set_ylabel("Aantal klachten", color='white')
        plt.xticks(rotation=45)
        st.pyplot(fig)

if st.session_state.get("data_ok", False):
    st.header("📊 Werkverdeling per team")

    df = st.session_state["data"].copy()
    df["datum"] = pd.to_datetime(df["datum"], errors="coerce")
    df = df.dropna(subset=["datum"])

    # Filters
    col1, col2 = st.columns([1, 3])
    with col1:
        hoofdcategorie_w = st.selectbox("Filter op hoofdcategorie (Workload)", ["Alles"] + sorted(df["hoofdcategorie"].dropna().unique()))
        subcategorie_w = st.selectbox("Filter op subcategorie (Workload)", ["Alles"] + sorted(df["subcategorie"].dropna().unique()))
        team_w = st.selectbox("Filter op team (Workload)", ["Alles"] + sorted(df["team"].dropna().unique()))
        wijk_w = st.selectbox("Filter op wijk (Workload)", ["Alles"] + sorted(df["wijk"].dropna().unique()))
        gebied_w = st.selectbox("Filter op gebied (Workload)", ["Alles"] + sorted(df["gebied"].dropna().unique()))
        bron_w = st.selectbox("Filter op bron (Workload)", ["Alles"] + sorted(df["bron"].dropna().unique()))

    with col2:
        tijdseenheid_w = st.radio("Tijdseenheid:", ["maand", "week"], horizontal=True)

    # Filters toepassen
    df_filtered = df.copy()
    if hoofdcategorie_w != "Alles":
        df_filtered = df_filtered[df_filtered["hoofdcategorie"] == hoofdcategorie_w]
    if subcategorie_w != "Alles":
        df_filtered = df_filtered[df_filtered["subcategorie"] == subcategorie_w]
    if team_w != "Alles":
        df_filtered = df_filtered[df_filtered["team"] == team_w]
    if wijk_w != "Alles":
        df_filtered = df_filtered[df_filtered["wijk"] == wijk_w]
    if gebied_w != "Alles":
        df_filtered = df_filtered[df_filtered["gebied"] == gebied_w]
    if bron_w != "Alles":
        df_filtered = df_filtered[df_filtered["bron"] == bron_w]

    # Groeperen per team én status
    df_grouped = df_filtered.groupby(["team", "status"]).size().unstack(fill_value=0)

    if df_grouped.empty:
        st.info("Geen meldingen gevonden voor deze combinatie van filters.")
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        df_grouped.plot(kind="bar", stacked=False, ax=ax)

        # Stijl
        fig.patch.set_facecolor("black")
        ax.set_facecolor("black")
        ax.set_title("Aantal meldingen per team en status", color='white')
        ax.set_xlabel("Team", color='white')
        ax.set_ylabel("Aantal klachten", color='white')
        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')
        ax.legend(title="Status", facecolor="black", edgecolor="white", labelcolor="white", title_fontsize=10)

        st.pyplot(fig)
