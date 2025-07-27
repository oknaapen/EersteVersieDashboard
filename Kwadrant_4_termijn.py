import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def kwadrant4(df):
    st.header("⏱️ Klachten binnen/buiten behandeltermijn")

    # Hulpfunctie om het aantal dagen uit een string te halen
    def extract_dagen(termijn):
        try:
            return int(str(termijn).split()[0])
        except (ValueError, IndexError):
            return None

    # Alleen klachten die zijn afgehandeld
    df_afgehandeld = df[df["status"] == "Afgehandelde klacht"].copy()

    # Conversie en berekening
    df_afgehandeld["behandelsduur"] = pd.to_numeric(df_afgehandeld["behandelsduur"], errors="coerce")
    df_afgehandeld["termijn_dagen"] = df_afgehandeld["behandeltermijn"].apply(extract_dagen)
    df_afgehandeld = df_afgehandeld.dropna(subset=["behandelsduur", "termijn_dagen"])

    # Als er geen meldingen zijn, stoppen
    if df_afgehandeld.empty:
        st.info("Geen meldingen beschikbaar voor deze combinatie.")
        return

    # Bereken of binnen de termijn
    df_afgehandeld["binnen_termijn"] = df_afgehandeld["behandelsduur"] <= df_afgehandeld["termijn_dagen"]

    # Filter op hoofdcategorie
    categorie_optie = st.selectbox(
        "Selecteer een hoofdcategorie:",
        ["Alles"] + sorted(df_afgehandeld["hoofdcategorie"].dropna().unique())
    )
    if categorie_optie != "Alles":
        df_afgehandeld = df_afgehandeld[df_afgehandeld["hoofdcategorie"] == categorie_optie]

    # Filter op subcategorie (alleen als kolom bestaat)
    if "subcategorie" in df_afgehandeld.columns:
        subcategorie_optie = st.selectbox(
            "Selecteer een subcategorie:",
            ["Alles"] + sorted(df_afgehandeld["subcategorie"].dropna().unique())
        )
        if subcategorie_optie != "Alles":
            df_afgehandeld = df_afgehandeld[df_afgehandeld["subcategorie"] == subcategorie_optie]
    else:
        subcategorie_optie = "Alles"

    # Aantallen binnen en buiten termijn
    binnen = df_afgehandeld["binnen_termijn"].sum()
    buiten = (~df_afgehandeld["binnen_termijn"]).sum()

    # Grafiek
    fig_termijn, ax_termijn = plt.subplots()
    fig_termijn.patch.set_facecolor("black")
    ax_termijn.set_facecolor("black")
    ax_termijn.pie(
        [binnen, buiten],
        labels=["Binnen termijn", "Buiten termijn"],
        autopct="%1.1f%%",
        colors=["limegreen", "red"],
        textprops={'color': 'white'},
        startangle=90
    )

    # Titel opbouwen
    titel = "Binnen/buiten behandeltermijn"
    if categorie_optie != "Alles":
        titel += f" ({categorie_optie})"
    if subcategorie_optie != "Alles":
        titel += f" - {subcategorie_optie}"
    ax_termijn.set_title(titel, color="white")
    ax_termijn.axis("equal")

    # Resultaten tonen
    st.pyplot(fig_termijn)
    st.markdown(f"**Binnen termijn:** {binnen} meldingen")
    st.markdown(f"**Buiten termijn:** {buiten} meldingen")

    # Voor later gebruik in export
    st.session_state["grafiek_kwadrant6"] = fig_termijn

