import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from bijlage import subcategorie_dict
import seaborn as sns

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
                df_schoon = df.dropna(subset=["hoofdcategorie", "subcategorie", "bron"])
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

if st.session_state.get("data_ok", False):

    if st.session_state.get("data_ok", False):
        df = st.session_state["data"].copy()
        df["datum"] = pd.to_datetime(df["datum"], errors='coerce')
        df = df.dropna(subset=["datum"])

        st.subheader("📊 Overzicht: Aantallen en Workload per team")

        # Maak twee kolommen naast elkaar
        col_links, col_rechts = st.columns([5, 5])

        # ===================== KWADRANT 1: AANTALLEN ===================== #

        with col_links:
            st.markdown("### 📈 Klachten in de tijd")
            col_links_2, col_rechts_2 = st.columns([5, 5])
            with col_links_2:
            # --- Keuzeknoppen voor weergave ---
                weergave_optie = st.radio("Kies weergave:", ["Lijngrafiek", "Verhoudingen", "Kaart"], horizontal=True)
            with col_rechts_2:
                tijdseenheid = st.radio("Toon per:", ["maand", "week"], horizontal=True)

            # --- Filters ---
            hoofdcategorie = st.selectbox("Hoofdcategorie", ["Alles"] + sorted(df["hoofdcategorie"].dropna().unique()))

            if hoofdcategorie in subcategorie_dict:
                sub_opties = ["Alles"] + subcategorie_dict[hoofdcategorie]
            else:
                sub_opties = ["Alles"] + sorted(df["subcategorie"].dropna().unique())
            subcategorie = st.selectbox("Subcategorie", sub_opties)
            team = st.selectbox("Team", ["Alles"] + sorted(df["team"].dropna().unique()))
            wijk = st.selectbox("Wijk", ["Alles"] + sorted(df["wijk"].dropna().unique()))
            gebied = st.selectbox("Gebied", ["Alles"] + sorted(df["gebied"].dropna().unique()))
            bron = st.selectbox("Bron", ["Alles"] + sorted(df["bron"].dropna().unique()))


            # --- Filteren ---
            df1 = df.copy()
            if hoofdcategorie != "Alles":
                df1 = df1[df1["hoofdcategorie"] == hoofdcategorie]
            if subcategorie != "Alles":
                df1 = df1[df1["subcategorie"] == subcategorie]
            if team != "Alles":
                df1 = df1[df1["team"] == team]
            if wijk != "Alles":
                df1 = df1[df1["wijk"] == wijk]
            if gebied != "Alles":
                df1 = df1[df1["gebied"] == gebied]
            if bron != "Alles":
                df1 = df1[df1["bron"] == bron]

            # # Tijdkolom maken
            if tijdseenheid == "week":
                df1["tijd"] = df1["datum"].dt.to_period("W").astype(str)
                xlabel = "Week"


            if weergave_optie == "Lijngrafiek":
                if tijdseenheid == "maand":
                    st.markdown("#### 📋 Totaal aantal meldingen per hoofdcategorie (weergave per Maand)")

                    totaal_per_categorie = df1["hoofdcategorie"].value_counts()

                    if totaal_per_categorie.empty:
                        st.info("Geen meldingen gevonden.")
                    else:
                        for categorie, aantal in totaal_per_categorie.items():
                            st.metric(label=categorie, value=int(aantal))
                            for categorie, aantal in totaal_per_categorie.items():
                                st.metric(label=categorie, value=int(aantal))

                                # === Extra: Cirkel en tabel per subcategorie van de gekozen hoofdcategorie ===
                                if hoofdcategorie != "Alles":
                                    st.markdown(f"#### 📊 Verdeling binnen '{hoofdcategorie}'")

                                    df_sub = df1[df1["hoofdcategorie"] == hoofdcategorie]
                                    subverdeling = df_sub["subcategorie"].value_counts()

                                    if subverdeling.empty:
                                        st.info("Geen subcategorieën gevonden.")
                                    else:
                                        # Twee kolommen: links cirkel, rechts tabel
                                        cirkel_col, tabel_col = st.columns(2)

                                        with cirkel_col:
                                            fig, ax = plt.subplots()
                                            ax.pie(subverdeling, labels=subverdeling.index, autopct="%1.1f%%",
                                                   startangle=90, textprops={'color': 'white'})
                                            ax.set_title("Subcategorieën binnen hoofdcategorie", color="white")
                                            fig.patch.set_facecolor("black")
                                            ax.set_facecolor("black")
                                            st.pyplot(fig)

                                        with tabel_col:
                                            st.markdown("##### 📋 Aantal meldingen per subcategorie")
                                            st.dataframe(subverdeling.rename("Aantal").reset_index().rename(
                                                columns={"index": "Subcategorie"}), use_container_width=True)

                        st.session_state["grafiek_kwadrant1"] = None  # Geen grafiek opslaan

                else:
                    tijdlijn = df1["tijd"].value_counts().sort_index()
                    if tijdlijn.empty:
                        st.info("Geen meldingen gevonden.")
                    else:
                        fig1, ax1 = plt.subplots()
                        fig1.patch.set_facecolor('black')
                        ax1.plot(tijdlijn.index, tijdlijn.values, marker='o', color='cyan')
                        ax1.set_title(f"Aantal klachten per {tijdseenheid}", color='white')
                        ax1.set_xlabel(xlabel, color='white')
                        ax1.set_ylabel("Aantal klachten", color='white')
                        ax1.set_facecolor("black")
                        ax1.tick_params(axis='x', colors='white', rotation=45)
                        ax1.tick_params(axis='y', colors='white')
                        st.pyplot(fig1, use_container_width=True)
                        st.session_state["grafiek_kwadrant1"] = fig1


            elif weergave_optie == "Verhoudingen":
                verdeling = df1["hoofdcategorie"].value_counts()
                if verdeling.empty:
                    st.info("Geen meldingen gevonden.")
                else:
                    fig2, ax2 = plt.subplots()
                    fig2.patch.set_facecolor("black")
                    ax2.pie(verdeling, labels=verdeling.index, autopct="%1.1f%%", textprops={'color': 'white'})
                    ax2.set_title("Verdeling meldingen per hoofdcategorie", color='white')
                    st.pyplot(fig2, use_container_width=True)
                    st.session_state["grafiek_kwadrant2"] = fig2

            elif weergave_optie == "Kaart":
                gebied_coords = {
                    "Woensel Noord": (6, 9),
                    "Woensel Zuid": (6, 6),
                    "Strijp": (2, 5),
                    "Centrum": (6.25, 4),
                    "Stratum": (7, 2),
                    "Tongelre": (8, 5),
                    "Gestel": (5, 2),
                }
                # Tellen per gebied
                gebied_counts = df1["gebied"].value_counts()

                # Kaart laden
                kaart_img = plt.imread("eindhoven.jpg")
                fig3, ax3 = plt.subplots(figsize=(8, 8))
                ax3.imshow(kaart_img, extent=[0, 10, 0, 10])
                ax3.set_facecolor("black")
                ax3.axis("off")
                st.session_state["grafiek_kwadrant3"] = fig3

                # Cirkels tekenen
                for gebied, (x, y) in gebied_coords.items():
                    aantal = gebied_counts.get(gebied, 0)
                    if aantal > 0:
                        ax3.scatter(x, y, s=aantal * 10, alpha=0.6, color="cyan", edgecolors="white", linewidths=1.5)
                        ax3.text(x, y + 0.3, f"{gebied}\n{aantal}", ha="center", va="bottom", color="white", fontsize=9)

                st.pyplot(fig3, use_container_width=True)

        # ===================== KWADRANT 2: WORKLOAD ===================== #

        with col_rechts:
            st.markdown("### 🧱 Workload per team")
            hoofdcategorie_w = st.selectbox("Hoofdcategorie (Workload)",
                                            ["Alles"] + sorted(df["hoofdcategorie"].dropna().unique()))
            subcategorie_w = st.selectbox("Subcategorie (Workload)",
                                          ["Alles"] + sorted(df["subcategorie"].dropna().unique()))
            team_w = st.selectbox("Team (Workload)", ["Alles"] + sorted(df["team"].dropna().unique()))
            wijk_w = st.selectbox("Wijk (Workload)", ["Alles"] + sorted(df["wijk"].dropna().unique()))
            gebied_w = st.selectbox("Gebied (Workload)", ["Alles"] + sorted(df["gebied"].dropna().unique()))
            bron_w = st.selectbox("Bron (Workload)", ["Alles"] + sorted(df["bron"].dropna().unique()))

            df2 = df.copy()
            if hoofdcategorie_w != "Alles":
                df2 = df2[df2["hoofdcategorie"] == hoofdcategorie_w]
            if subcategorie_w != "Alles":
                df2 = df2[df2["subcategorie"] == subcategorie_w]
            if team_w != "Alles":
                df2 = df2[df2["team"] == team_w]
            if wijk_w != "Alles":
                df2 = df2[df2["wijk"] == wijk_w]
            if gebied_w != "Alles":
                df2 = df2[df2["gebied"] == gebied_w]
            if bron_w != "Alles":
                df2 = df2[df2["bron"] == bron_w]

            df_grouped = df2.groupby(["team", "status"]).size().unstack(fill_value=0)

            if df_grouped.empty:
                st.info("Geen meldingen gevonden.")
            else:
                fig2, ax2 = plt.subplots(figsize=(8, 5))
                df_grouped.plot(kind="bar", stacked=False, ax=ax2)

                fig2.patch.set_facecolor("black")
                ax2.set_facecolor("black")
                ax2.set_title("Aantal meldingen per team en status", color='white')
                ax2.set_xlabel("Team", color='white')
                ax2.set_ylabel("Aantal klachten", color='white')
                ax2.tick_params(axis='x', colors='white', rotation=45)
                ax2.tick_params(axis='y', colors='white')
                ax2.legend(title="Status", facecolor="black", edgecolor="white", labelcolor="white", title_fontsize=10)
                st.pyplot(fig2, use_container_width=True)
                st.session_state["grafiek_kwadrant4"] = fig2

        # ===================== KWADRANT 3: Tevredenheid ======
        if st.session_state.get("data_ok", False):
            df = st.session_state["data"]
            # Maak linker- en rechterkolom aan
            col_links, col_rechts = st.columns(2)

            with col_links:
                    st.header("🧭 Klantreis per team")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        geselecteerd_team = st.selectbox("Filter op team",["Alles"] + sorted(df["team"].dropna().unique()))
                    with col2:
                        geselecteerde_termijn = st.selectbox("Filter op behandeltermijn",["Alles"] + sorted(df["behandeltermijn"].dropna().unique()))
                    with col3:
                        geselecteerde_hoofdcategorie = st.selectbox("Filter op hoofdcategorie", ["Alles"] + sorted(df["hoofdcategorie"].dropna().unique()))

                    df_filtered = df.copy()

                    if geselecteerd_team != "Alles":
                        df_filtered  = df_filtered[df_filtered["team"] == geselecteerd_team]
                    if geselecteerde_termijn != "Alles":
                        df_filtered  = df_filtered[df_filtered["behandeltermijn"] == geselecteerde_termijn]
                    if geselecteerde_hoofdcategorie != "Alles":
                        df_filtered  = df_filtered[df_filtered["hoofdcategorie"] == geselecteerde_hoofdcategorie]

                    df_counts = df_filtered.groupby(["team", "tevredenheid"]).size().unstack(fill_value=0)

                    if df_counts.empty:
                        st.info("Geen data beschikbaar voor deze combinatie van filters.")
                    else:
                        gewenste_volgorde = ["Zeer ontevreden", "Ontevreden", "Neutraal", "Tevreden", "Zeer tevreden", "Onbekend"]
                        for cat in gewenste_volgorde:
                            if cat not in df_counts.columns:
                                df_counts[cat] = 0

                        df_counts = df_counts[gewenste_volgorde]

                        fig, ax = plt.subplots(figsize=(10, 5))
                        bottom = None
                        kleuren = ["darkred", "red", "gray", "limegreen", "darkgreen", "orange"]
                        ax.set_title("Tevredenheid per team (volledige verdeling)")
                        ax.set_xlabel("Aantal klachten", color='white')
                        ax.set_ylabel("Team", color='white')
                        ax.legend()

                        for i, cat in enumerate(gewenste_volgorde):
                            ax.barh(df_counts.index, df_counts[cat], left=bottom, label=cat, color=kleuren[i])
                            bottom = df_counts[cat] if bottom is None else bottom + df_counts[cat]
                        st.pyplot(fig)
                        st.session_state["grafiek_kwadrant5"] = fig

                # ===== RECHTERKWADRANT: Wijzigingen (ML) =====
            with col_rechts:
                    st.header("🤖 Aantal keer correct afgehandeld (Machine Learning)")

                    wijzigingswaarden = df["wijziging"].dropna().astype(int)
                    aantallen = wijzigingswaarden.value_counts().sort_index()

                    labels = [
                        "In één keer goed" if i == 1 else
                        "In twee keer goed" if i == 2 else
                        "In drie keer goed" if i == 3 else
                        f"In {i} keer goed"
                        for i in aantallen.index
                    ]

                    fig, ax = plt.subplots()
                    ax.pie(aantallen, labels=labels, autopct="%1.1f%%", startangle=90,
                           colors=["green", "orange", "red"])
                    ax.set_title("Hoe vaak is een melding correct afgehandeld?")
                    ax.axis("equal")
                    st.pyplot(fig)
                    st.session_state["grafiek_kwadrant6"] = fig

            # Stijl voor groene knop met zwarte tekst
            custom_button = """
            <style>
            div.stButton > button {
                background-color: #32CD32;  /* limegreen */
                color: black;
                font-weight: bold;
                border: none;
                padding: 0.5em 1em;
                border-radius: 5px;
            }
            </style>
            """
            st.markdown(custom_button, unsafe_allow_html=True)

            # Knop zelf
            if st.button("📄 Genereer PDF"):

                from fpdf import FPDF
                import tempfile
                import os
                from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()


                def add_fig_to_pdf(pdf, fig, titel):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                        canvas = FigureCanvas(fig)
                        canvas.print_png(tmpfile.name)
                        tmpfile.close()
                        pdf.set_font("Arial", "B", 12)
                        pdf.cell(0, 10, titel, ln=True)
                        pdf.image(tmpfile.name, w=180)  # breedte 180 mm voor bijna volle pagina
                        os.unlink(tmpfile.name)


                if "grafiek_kwadrant1" in st.session_state:
                    add_fig_to_pdf(pdf, st.session_state["grafiek_kwadrant1"], " Klachten in de tijd")

                if "grafiek_kwadrant3" in st.session_state:
                    add_fig_to_pdf(pdf, st.session_state["grafiek_kwadrant3"], "Klantreis per team")

                if "grafiek_kwadrant4" in st.session_state:
                    add_fig_to_pdf(pdf, st.session_state["grafiek_kwadrant4"], " Aantal keer correct afgehandeld")

                # Downloadlink tonen
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as output:
                    pdf.output(output.name)
                    with open(output.name, "rb") as file:
                        st.download_button("📥 Download PDF", file, file_name="dashboard.pdf", mime="application/pdf")
