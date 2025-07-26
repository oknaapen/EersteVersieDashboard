import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def kwadrant3(df):
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

            # === Analyse: tevredenheidsscore per team ===
            df_tevreden = df_filtered.copy()
            df_tevreden["tevreden"] = df_tevreden["tevredenheid"].isin(["Tevreden", "Zeer tevreden"])
            df_tevreden["ontevreden"] = df_tevreden["tevredenheid"].isin(["Ontevreden", "Zeer ontevreden"])

            score_per_team = df_tevreden.groupby("team").agg(
                totaal=("tevreden", "count"),
                tevreden=("tevreden", "sum"),
                ontevreden=("ontevreden", "sum")
            ).reset_index()

            score_per_team["% tevreden"] = round(score_per_team["tevreden"] / score_per_team["totaal"] * 100, 1)
            score_per_team["% ontevreden"] = round(score_per_team["ontevreden"] / score_per_team["totaal"] * 100, 1)

            top_tevreden = score_per_team.sort_values(by="% tevreden", ascending=False).head(1)
            top_ontevreden = score_per_team.sort_values(by="% ontevreden", ascending=False).head(1)

            # === Algemene conclusie bovenaan ===
            if not df_filtered.empty:
                totaal = df_filtered.shape[0]
                meest_actief_team = df_filtered["team"].value_counts().idxmax()
                meest_actief_team_aantal = df_filtered["team"].value_counts().max()
                meest_voorkomende_tevredenheid = df_filtered["tevredenheid"].value_counts().idxmax()
                onbekend_perc = round(
                    df_filtered["tevredenheid"].isin(["Onbekend", "Neutraal"]).sum() / totaal * 100, 1
                )
                aantal_teams = df_filtered["team"].nunique()

            if not top_tevreden.empty and not top_ontevreden.empty:
                team_tev = top_tevreden.iloc[0]["team"]
                perc_tev = top_tevreden.iloc[0]["% tevreden"]
                team_ontev = top_ontevreden.iloc[0]["team"]
                perc_ontev = top_ontevreden.iloc[0]["% ontevreden"]

                st.markdown("### 🧾 Samenvatting tevredenheid per team")
                st.info(f"""
                - Over **{team_tev}** zijn klanten het meest tevreden (**{perc_tev}% tevreden of zeer tevreden**).
                - Over **{team_ontev}** zijn klanten het minst tevreden (**{perc_ontev}% ontevreden of zeer ontevreden**).
                """)

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