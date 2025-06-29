import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from bijlage import subcategorie_dict
from bijlage import kolom_aliases
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

st.title("Meldingen Dashboard")

st.markdown("<h3 style ='text-align: left; color: #2E8B57;'>Upload hier een CSV-bestand...</h3>",
            unsafe_allow_html=True)

uploaded_file = st.file_uploader("Hier kun u een CSV bestand uploaden", type=["csv"])

if uploaded_file:
    voorbeeld = st.button("Zie een voorbeeld")
    if voorbeeld:
        df = pd.read_csv(uploaded_file)
        st.write(df.head())
    try:  #
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()  # Kolomnamen opschonen
        # Slimme vervanging van kolomnamen
        nieuwe_kolommen = []
        for col in df.columns:
            if col in kolom_aliases:
                nieuwe_kolommen.append(kolom_aliases[col])
            else:
                nieuwe_kolommen.append(col)
        df.columns = nieuwe_kolommen
        st.info("Kolomnamen zijn automatisch opgeschoond en gestandaardiseerd.")
        # Vereiste kolommen
        vereiste_kolommen = [
            "indexnummer", "klachtnummer", "naam", "email", "telefoon", "datum",
            "hoofdcategorie", "subcategorie", "behandeltermijn", "status", "bron",
            "gebied", "wijk", "tevredenheid", "team", "wijziging", "behandelsduur"
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

        st.markdown("""
            <style>
            div[role="radiogroup"] > label > div[data-testid="stMarkdownContainer"] > p {
                color: white !important;
                font-weight: bold;
            }
            </style>
        """, unsafe_allow_html=True)

        # ===================== KWADRANT 1: AANTALLEN ===================== #
        st.markdown("""
            <style>
            div[role="radiogroup"] label {
                color: white !important;
            }
            div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
                color: white !important;
            }
            </style>
        """, unsafe_allow_html=True)

        with col_links:
            st.markdown("### 📈 Klachten in de tijd")

            # --- Keuzeknoppen voor weergave ---
            weergave_optie = st.radio("Kies uw visualisatie:", [
                "📊 Totaal aantal meldingen over de maand",
                "📈 Verdeling",
                "🗺️ Meldingen op de kaart",
                "📋 Totaal aantal meldingen per hoofdcategorie",
                "🏘️ Meldingen per wijk",
                "❌ Wis selectie"
            ], horizontal=False)

            # --- Filters ---
            st.markdown("### 🔍 Filters")
            hoofdcategorie = st.selectbox("Hoofdcategorie", ["Alles"] + sorted(df["hoofdcategorie"].dropna().unique()))
            if hoofdcategorie in subcategorie_dict:
                sub_opties = ["Alles"] + subcategorie_dict[hoofdcategorie]
            else:
                sub_opties = ["Alles"] + sorted(df["subcategorie"].dropna().unique())
            subcategorie = st.selectbox("Subcategorie", sub_opties)
            bron = st.selectbox("Bron", ["Alles"] + sorted(df["bron"].dropna().unique()))

            # Filter toepassen
            df1 = df.copy()
            if hoofdcategorie != "Alles":
                df1 = df1[df1["hoofdcategorie"] == hoofdcategorie]
            if subcategorie != "Alles":
                df1 = df1[df1["subcategorie"] == subcategorie]
            if bron != "Alles":
                df1 = df1[df1["bron"] == bron]

            # Weektijdkolom aanmaken
            df1["tijd"] = df1["datum"].dt.strftime("%G-W%V (%d-%m-%Y)")

            # === 📊 Lijngrafiek meldingen over tijd ===
            if weergave_optie in ["📊 Totaal aantal meldingen over de maand", "❌ Wis selectie"]:
                tijdlijn = df1["tijd"].value_counts().sort_index()
                if tijdlijn.empty:
                    st.info("Geen meldingen gevonden.")
                else:
                    fig1, ax1 = plt.subplots()
                    fig1.patch.set_facecolor('black')
                    ax1.plot(tijdlijn.index, tijdlijn.values, color='cyan', linewidth=2)
                    ax1.scatter(tijdlijn.index, tijdlijn.values, color='red', edgecolors='white', zorder=5)
                    ax1.set_title("Totaal aantal klachten per week", color='white')
                    ax1.set_xlabel("Weeknummer (Datum)", color='white')
                    ax1.set_ylabel("Aantal klachten", color='white')
                    ax1.set_facecolor("black")

                    x_values = list(tijdlijn.index)
                    if len(x_values) >= 4:
                        indices = [0, len(x_values) // 3, 2 * len(x_values) // 3, len(x_values) - 1]
                        ax1.set_xticks([x_values[i] for i in indices])
                        ax1.set_xticklabels([x_values[i] for i in indices], rotation=90, color='white')
                    else:
                        ax1.set_xticklabels(x_values, rotation=90, color='white')

                    ax1.tick_params(axis='y', colors='white')
                    st.pyplot(fig1, use_container_width=True)
                    st.session_state["grafiek_kwadrant1"] = fig1

            # === 📈 Verdeling per hoofdcategorie ===
            elif weergave_optie == "📈 Verdeling":
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

                    if hoofdcategorie != "Alles":
                        st.markdown(f"#### 📊 Subverdeling binnen '{hoofdcategorie}'")
                        subverdeling = df1[df1["hoofdcategorie"] == hoofdcategorie]["subcategorie"].value_counts()
                        if not subverdeling.empty:
                            st.bar_chart(subverdeling)

                    st.markdown("#### 🧭 Verdeling per bron")
                    bronverdeling = df1["bron"].value_counts()
                    if not bronverdeling.empty:
                        fig_bron, ax_bron = plt.subplots()
                        fig_bron.patch.set_facecolor("black")
                        ax_bron.pie(bronverdeling, labels=bronverdeling.index, autopct="%1.1f%%",
                                    textprops={'color': 'white'})
                        ax_bron.set_title("Verdeling meldingen per bron", color='white')
                        st.pyplot(fig_bron, use_container_width=True)

            # === 🗺️ Kaart met meldingen ===
            elif weergave_optie == "🗺️ Meldingen op de kaart":
                gebied_coords = {
                    "Woensel Noord": (6, 9),
                    "Woensel Zuid": (6, 6),
                    "Strijp": (2, 5),
                    "Centrum": (6.25, 4),
                    "Stratum": (7, 2),
                    "Tongelre": (8, 5),
                    "Gestel": (5, 2),
                }
                gebied_counts = df1["gebied"].value_counts()
                kaart_img = plt.imread("eindhoven.jpg")
                fig3, ax3 = plt.subplots(figsize=(8, 8))
                ax3.imshow(kaart_img, extent=[0, 10, 0, 10])
                ax3.set_facecolor("black")
                ax3.axis("off")
                st.session_state["grafiek_kwadrant3"] = fig3
                for gebied, (x, y) in gebied_coords.items():
                    aantal = gebied_counts.get(gebied, 0)
                    if aantal > 0:
                        ax3.scatter(x, y, s=aantal * 10, alpha=0.6, color="cyan", edgecolors="white", linewidths=1.5)
                        ax3.text(x, y + 0.3, f"{gebied}\n{aantal}", ha="center", va="bottom", color="white", fontsize=9)
                st.pyplot(fig3, use_container_width=True)

            # === 📋 Metrics per hoofdcategorie ===
            elif weergave_optie == "📋 Totaal aantal meldingen per hoofdcategorie":
                st.markdown("#### 📋 Totaal aantal meldingen per hoofdcategorie")
                totaal_per_categorie = df1["hoofdcategorie"].value_counts()
                if totaal_per_categorie.empty:
                    st.info("Geen meldingen gevonden.")
                else:
                    for categorie, aantal in totaal_per_categorie.items():
                        st.metric(label=categorie, value=int(aantal))
                    if hoofdcategorie != "Alles":
                        st.markdown(f"#### 📊 Verdeling binnen '{hoofdcategorie}'")
                        df_sub = df1[df1["hoofdcategorie"] == hoofdcategorie]
                        subverdeling = df_sub["subcategorie"].value_counts()
                        if subverdeling.empty:
                            st.info("Geen subcategorieën gevonden.")
                        else:
                            cirkel_col, tabel_col = st.columns(2)
                            with cirkel_col:
                                fig, ax = plt.subplots()
                                ax.pie(subverdeling, labels=subverdeling.index, autopct="%1.1f%%", startangle=90,
                                       textprops={'color': 'white'})
                                ax.set_title("Subcategorieën binnen hoofdcategorie", color="white")
                                fig.patch.set_facecolor("black")
                                ax.set_facecolor("black")
                                st.pyplot(fig)
                            with tabel_col:
                                st.markdown("##### 📋 Aantal meldingen per subcategorie")
                                st.dataframe(subverdeling.rename("Aantal").reset_index().rename(
                                    columns={"index": "Subcategorie"}), use_container_width=True)
                st.session_state["grafiek_kwadrant1"] = None

            # === 🏘️ Meldingen per wijk ===
            elif weergave_optie == "🏘️ Meldingen per wijk":
                st.markdown("#### 🏘️ Aantal meldingen per wijk")
                wijk_verdeling = df1["wijk"].value_counts()
                if wijk_verdeling.empty:
                    st.info("Geen meldingen gevonden.")
                else:
                    fig4, ax4 = plt.subplots()
                    fig4.patch.set_facecolor("black")
                    ax4.bar(wijk_verdeling.index, wijk_verdeling.values, color="cyan")
                    ax4.set_title("Aantal klachten per wijk", color="white")
                    ax4.set_xlabel("Wijk", color="white")
                    ax4.set_ylabel("Aantal klachten", color="white")
                    ax4.set_facecolor("black")
                    ax4.tick_params(axis='x', colors='white', rotation=45)
                    ax4.tick_params(axis='y', colors='white')
                    st.pyplot(fig4, use_container_width=True)

        # ===================== KWADRANT 2: WORKLOAD ===================== #

        with col_rechts:
            st.markdown("### 🧱 Workload per team")

            # Keuze voor weergave
            workload_optie = st.radio("Selecteer een weergave:", [
                "📊 Staafdiagram per status",
                "📋 Totaal aantal klachten per team"
            ], horizontal=False)

            # Filter op status
            status_filter = st.selectbox("Status", ["Alles"] + sorted(df["status"].dropna().unique()))

            df2 = df.copy()
            if status_filter != "Alles":
                df2 = df2[df2["status"] == status_filter]

            if workload_optie == "📊 Staafdiagram per status":
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
                    ax2.tick_params(axis='x', colors='white', rotation=75)
                    ax2.tick_params(axis='y', colors='white')
                    ax2.legend(title="Status", facecolor="black", edgecolor="white", labelcolor="white",
                               title_fontsize=10)
                    st.pyplot(fig2, use_container_width=True)
                    st.session_state["grafiek_kwadrant4"] = fig2

            elif workload_optie == "📋 Totaal aantal klachten per team":
                totaal_per_team = df2["team"].value_counts().sort_values(ascending=False)
                if totaal_per_team.empty:
                    st.info("Geen meldingen gevonden.")
                else:
                    st.markdown("#### 📋 Aantal klachten per team")
                    for team, aantal in totaal_per_team.items():
                        st.metric(label=team, value=int(aantal))

        # ===================== KWADRANT 3: Tevredenheid ======
        # ===================== KWADRANT 3: Tevredenheid ======
        if st.session_state.get("data_ok", False):
            df = st.session_state["data"]

            # Extra optie: reset alle filters
            reset_optie = st.radio("Filteroptie:", ["✅ Alles tonen", "🔎 Filters gebruiken"], horizontal=True)

            # Maak linker- en rechterkolom aan
            col_links, col_rechts = st.columns(2)

            with col_links:
                st.header("🧭 Klantreis per team")

                if reset_optie == "🔎 Filters gebruiken":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        geselecteerd_team = st.selectbox("Filter op team",
                                                         ["Alles"] + sorted(df["team"].dropna().unique()))
                    with col2:
                        geselecteerde_termijn = st.selectbox("Filter op behandeltermijn", ["Alles"] + sorted(
                            df["behandeltermijn"].dropna().unique()))
                    with col3:
                        geselecteerde_hoofdcategorie = st.selectbox("Filter op hoofdcategorie", ["Alles"] + sorted(
                            df["hoofdcategorie"].dropna().unique()))
                else:
                    geselecteerd_team = geselecteerde_termijn = geselecteerde_hoofdcategorie = "Alles"

                df_filtered = df.copy()

                if geselecteerd_team != "Alles":
                    df_filtered = df_filtered[df_filtered["team"] == geselecteerd_team]
                if geselecteerde_termijn != "Alles":
                    df_filtered = df_filtered[df_filtered["behandeltermijn"] == geselecteerde_termijn]
                if geselecteerde_hoofdcategorie != "Alles":
                    df_filtered = df_filtered[df_filtered["hoofdcategorie"] == geselecteerde_hoofdcategorie]

                gewenste_volgorde = ["Zeer ontevreden", "Ontevreden", "Neutraal", "Tevreden", "Zeer tevreden",
                                     "Onbekend"]

                # Toevoegen van radioknop voor weergave
                weergave_tevredenheid = st.radio("Kies uw weergave:", [
                    "📊 Tevredenheid per team (grafiek)",
                    "🏆 Top 10 (per tevredenheidsniveau)"
                ], horizontal=False)

                # Extra filter op tevredenheid onder de st.radio
                tevredenheidsfilter = st.selectbox("Filter op tevredenheidsniveau (voor top 10 weergave)",
                                                   gewenste_volgorde)

                if weergave_tevredenheid == "📊 Tevredenheid per team (grafiek)":
                    df_counts = df_filtered.groupby(["team", "tevredenheid"]).size().unstack(fill_value=0)
                    for cat in gewenste_volgorde:
                        if cat not in df_counts.columns:
                            df_counts[cat] = 0
                    df_counts = df_counts[gewenste_volgorde]

                    if df_counts.empty:
                        st.info("Geen data beschikbaar voor deze combinatie van filters.")
                    else:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        fig.patch.set_facecolor("black")
                        ax.set_facecolor("black")
                        bottom = None
                        kleuren = ["darkred", "red", "gray", "limegreen", "darkgreen", "orange"]
                        ax.set_title("Tevredenheid per team (volledige verdeling)", color="white")
                        ax.set_xlabel("Aantal klachten", color='white')
                        ax.set_ylabel("Team", color='white')

                        for i, cat in enumerate(gewenste_volgorde):
                            ax.barh(df_counts.index, df_counts[cat], left=bottom, label=cat, color=kleuren[i])
                            bottom = df_counts[cat] if bottom is None else bottom + df_counts[cat]

                        ax.tick_params(axis='x', colors='white')
                        ax.tick_params(axis='y', colors='white')
                        ax.legend(title="Tevredenheid", facecolor="black", edgecolor="white", labelcolor="white")
                        st.pyplot(fig)
                        st.session_state["grafiek_kwadrant5"] = fig

                elif weergave_tevredenheid == "🏆 Top 10 (per tevredenheidsniveau)":
                    st.markdown(f"#### 🏆 Top 10 meldingen met '{tevredenheidsfilter}'")
                    col_team, col_cat = st.columns(2)

                    with col_team:
                        top_teams = df_filtered[df_filtered["tevredenheid"] == tevredenheidsfilter][
                            "team"].value_counts().head(10)
                        st.markdown("##### Teams")
                        for team, aantal in top_teams.items():
                            st.metric(label=team, value=aantal)

                    with col_cat:
                        top_cats = df_filtered[df_filtered["tevredenheid"] == tevredenheidsfilter][
                            "hoofdcategorie"].value_counts().head(10)
                        st.markdown("##### Hoofdcategorieën")
                        for cat, aantal in top_cats.items():
                            st.metric(label=cat, value=aantal)



            # ===== RECHTERKWADRANT: Wijzigingen (ML) =====
    with col_rechts:
        st.header("⏱️ Klachten binnen/buiten behandeltermijn")

        # Filter op status
        df_afgehandeld = df[df["status"] == "Afgehandelde klacht"].copy()
        df_afgehandeld["behandelsduur"] = pd.to_numeric(df_afgehandeld["behandelsduur"], errors="coerce")


        # Extract aantal dagen uit behandeltermijn
        def extract_dagen(termijn):
            try:
                return int(termijn.split()[0])
            except:
                return None


        df_afgehandeld["termijn_dagen"] = df_afgehandeld["behandeltermijn"].apply(extract_dagen)
        df_afgehandeld = df_afgehandeld.dropna(subset=["behandelsduur", "termijn_dagen"])
        df_afgehandeld["binnen_termijn"] = df_afgehandeld["behandelsduur"] <= df_afgehandeld["termijn_dagen"]

        # Selectie per hoofdcategorie via selectbox
        categorie_optie = st.selectbox("Selecteer een hoofdcategorie:",
                                       ["Alles"] + sorted(df_afgehandeld["hoofdcategorie"].dropna().unique()))

        if categorie_optie != "Alles":
            df_afgehandeld = df_afgehandeld[df_afgehandeld["hoofdcategorie"] == categorie_optie]

        # Selectie per subcategorie gebaseerd op hoofdcategorie
        beschikbare_subcategorieen = df_afgehandeld["subcategorie"].dropna().unique()
        subcategorie_optie = st.selectbox("Selecteer een subcategorie:",
                                          ["Alles"] + sorted(beschikbare_subcategorieen))

        if subcategorie_optie != "Alles":
            df_afgehandeld = df_afgehandeld[df_afgehandeld["subcategorie"] == subcategorie_optie]

        binnen = df_afgehandeld["binnen_termijn"].sum()
        buiten = (~df_afgehandeld["binnen_termijn"]).sum()

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
        titel = "Binnen/buiten behandeltermijn"
        if categorie_optie != "Alles":
            titel += f" ({categorie_optie})"
            if subcategorie_optie != "Alles":
                titel += f" - {subcategorie_optie}"

        ax_termijn.set_title(titel, color="white")
        ax_termijn.axis("equal")

        st.pyplot(fig_termijn)
        st.markdown(f"**Binnen termijn:** {binnen} meldingen")
        st.markdown(f"**Buiten termijn:** {buiten} meldingen")

        st.session_state["grafiek_kwadrant6"] = fig_termijn

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
