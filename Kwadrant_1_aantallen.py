import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from bijlage import subcategorie_dict

def kwadrant1(df):
    st.header("📌 Analyse van meldingen")

    st.markdown("""
        <style>
        /* Maak de labels van de radioknoppen wit */
        div[role="radiogroup"] label {
            color: white !important;
        }

        /* Extra: pas tekst binnen de knoppen aan */
        div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
            color: white !important;
            font-weight: bold;
        }

        /* Extra: verander de selectiebolletjes naar wit */
        input[type="radio"] + div span {
            background-color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

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

    df1 = df.copy()
    if hoofdcategorie != "Alles":
        df1 = df1[df1["hoofdcategorie"] == hoofdcategorie]
    if subcategorie != "Alles":
        df1 = df1[df1["subcategorie"] == subcategorie]
    if bron != "Alles":
        df1 = df1[df1["bron"] == bron]

    df1["tijd"] = df1["datum"].dt.strftime("%G-W%V (%d-%m-%Y)")

    if df1.empty:
        st.warning("Geen meldingen gevonden voor deze filters.")
        return

    # 📊 Tijdlijn
    if weergave_optie in ["📊 Totaal aantal meldingen over de maand", "❌ Wis selectie"]:

        tijdlijn = df1["tijd"].value_counts().sort_index()
        dag_max = df1["datum"].dt.strftime("%A").value_counts().idxmax()

        # Conclusie
        week_max = tijdlijn.idxmax()

        totaal = tijdlijn.sum()

        st.markdown(f"""
            <div style='background-color:#1e90ff; padding:15px; border-radius:5px'>
                <p style='color:white; font-size:16px;'>
                - Aantal meldingen binnengekomen: <b>{totaal}</b><br>
                - Week met de meeste meldingen: <b>{week_max}</b><br>
                - Dag met de meeste meldingen: <b>{dag_max}</b>
                </p>
            </div>
        """, unsafe_allow_html=True)

        fig1, ax1 = plt.subplots()
        fig1.patch.set_facecolor('black')
        ax1.plot(tijdlijn.index, tijdlijn.values, color='cyan', linewidth=2)
        ax1.scatter(tijdlijn.index, tijdlijn.values, color='red', edgecolors='white', zorder=5)
        ax1.set_title("Totaal aantal klachten per week", color='white')
        ax1.set_xlabel("Weeknummer (Datum)", color='white')
        ax1.set_ylabel("Aantal klachten", color='white')
        ax1.set_facecolor("black")
        st.session_state["grafiek_kwadrant1"] = fig1

        x_values = list(tijdlijn.index)
        if len(x_values) >= 4:
            indices = [0, len(x_values) // 3, 2 * len(x_values) // 3, len(x_values) - 1]
            ax1.set_xticks([x_values[i] for i in indices])
            ax1.set_xticklabels([x_values[i] for i in indices], rotation=90, color='white')
        else:
            ax1.set_xticklabels(x_values, rotation=90, color='white')
        ax1.tick_params(axis='y', colors='white')
        st.pyplot(fig1, use_container_width=True)

    # 📈 Verdeling
    elif weergave_optie == "📈 Verdeling":
        verdeling = df1["hoofdcategorie"].value_counts()

        grootste = verdeling.idxmax()
        kleinste = verdeling.idxmin()
        st.info(f"""
               - Grootste verhouding: **{grootste}**
               - Kleinste verhouding: **{kleinste}**
               """)

        fig2, ax2 = plt.subplots()
        fig2.patch.set_facecolor("black")
        ax2.pie(verdeling, labels=verdeling.index, autopct="%1.1f%%", textprops={'color': 'white'})
        ax2.set_title("Verdeling meldingen per hoofdcategorie", color='white')
        st.pyplot(fig2, use_container_width=True)
        st.session_state["grafiek_kwadrant1"] = fig2

    # 🗺️ Kaart
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

        top_gebied = gebied_counts.idxmax()
        top_data = df1[df1["gebied"] == top_gebied]
        top_hoofd = top_data["hoofdcategorie"].value_counts().idxmax()
        top_sub = top_data["subcategorie"].value_counts().idxmax()
        st.info(f"""
                - Meeste klachten in: **{top_gebied}**
                - Hoofdcategorie: **{top_hoofd}**
                - Subcategorie: **{top_sub}**
                """)

        kaart_img = plt.imread("eindhoven.jpg")
        fig3, ax3 = plt.subplots(figsize=(8, 8))
        ax3.imshow(kaart_img, extent=[0, 10, 0, 10])
        ax3.set_facecolor("black")
        ax3.axis("off")
        for gebied, (x, y) in gebied_coords.items():
            aantal = gebied_counts.get(gebied, 0)
            if aantal > 0:
                ax3.scatter(x, y, s=aantal * 10, alpha=0.6, color="cyan", edgecolors="white", linewidths=1.5)
                ax3.text(x, y + 0.3, f"{gebied}\n{aantal}", ha="center", va="bottom", color="white", fontsize=9)
        st.pyplot(fig3, use_container_width=True)
        st.session_state["grafiek_kwadrant1"] = fig3

    # 📋 Per hoofdcategorie
    elif weergave_optie == "📋 Totaal aantal meldingen per hoofdcategorie":
        totaal_per_cat = df1["hoofdcategorie"].value_counts()
        for cat, aantal in totaal_per_cat.items():
            st.metric(label=cat, value=int(aantal))

        if hoofdcategorie != "Alles":
            subverdeling = df1[df1["hoofdcategorie"] == hoofdcategorie]["subcategorie"].value_counts()
            if not subverdeling.empty:
                st.bar_chart(subverdeling)
    # 🏘️ Per wijk
    elif weergave_optie == "🏘️ Meldingen per wijk":
        wijkverdeling = df1["wijk"].value_counts()

        top_wijk = wijkverdeling.idxmax()
        top_data = df1[df1["wijk"] == top_wijk]
        top_hoofd = top_data["hoofdcategorie"].value_counts().idxmax()
        top_sub = top_data["subcategorie"].value_counts().idxmax()
        st.info(f"""
                - Wijk met de meeste klachten: **{top_wijk}**
                - Hoofdcategorie: **{top_hoofd}**
                - Subcategorie: **{top_sub}**
                """)

        fig4, ax4 = plt.subplots()
        fig4.patch.set_facecolor("black")
        ax4.bar(wijkverdeling.index, wijkverdeling.values, color="cyan")
        ax4.set_title("Aantal klachten per wijk", color="white")
        ax4.set_xlabel("Wijk", color="white")
        ax4.set_ylabel("Aantal klachten", color="white")
        ax4.set_facecolor("black")
        ax4.tick_params(axis='x', colors='white', rotation=45)
        ax4.tick_params(axis='y', colors='white')
        st.pyplot(fig4, use_container_width=True)
        st.session_state["grafiek_kwadrant1"] = fig4




