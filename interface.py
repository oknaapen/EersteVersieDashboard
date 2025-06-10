import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from click import style

# Titel en introductie
st.title("Meldingen Dashboard")

st.markdown("""<h1 style ='text-align: center; color: #2E8B57;'> Upload hier een CSV-bestand met klachtenregistraties. Het bestand wordt automatisch gecontroleerd op geldigheid en volledigheid.</hi>""", unsafe_allow_html=True)

# Bestand uploaden
uploaded_file = st.file_uploader("Upload een CSV-bestand", type=["csv"])

if uploaded_file:
    try:
        # Proberen in te lezen
        df = pd.read_csv(uploaded_file)
        # Controleren op verplichte kolommen
        vereiste_kolommen = [
            "indexnummer", "klachtnummer", "naam", "email", "telefoon", "datum",
            "hoofdcategorie", "subcategorie", "behandeltermijn", "status", "bron",
            "gebied", "wijk", "tevredenheid", "team", "wijziging"
        ]

        if not all(kolom in df.columns for kolom in vereiste_kolommen):
            st.error("Het CSV-bestand mist één of meer verplichte kolommen. Controleer het formaat.")
        else:
            # Tellen van NaN/lege waarden
            totaal_rijen = df.shape[0]
            aantal_nan_rijen = df[df.isnull().any(axis=1)].shape[0]

            if aantal_nan_rijen / totaal_rijen < 0.5:
                st.error("Er zijn te veel ontbrekende waarden. Herzie het CSV-bestand.")
            else:
                # Rijen met ontbrekende waarden verwijderen
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
        st.error(f"Er ging iets mis bij het inlezen van het bestand: {e}")

