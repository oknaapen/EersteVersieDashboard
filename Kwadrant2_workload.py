import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# ===================== KWADRANT 2: WORKLOAD ===================== #
def kwadrant2(df):

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

            # Conclusie boven de grafiek
            if "Afgehandelde klacht" in df_grouped.columns:
                team_afgehandeld = df_grouped["Afgehandelde klacht"].idxmax()
                aantal_afgehandeld = df_grouped["Afgehandelde klacht"].max()
            else:
                team_afgehandeld = "n.v.t."
                aantal_afgehandeld = 0

            # Kijk of er open statussen zijn
            open_statusen = [col for col in df_grouped.columns if "Open" in col or "open" in col or "Bezig" in col]
            if open_statusen:
                df_grouped["Totaal open"] = df_grouped[open_statusen].sum(axis=1)
                team_open = df_grouped["Totaal open"].idxmax()
                aantal_open = df_grouped["Totaal open"].max()
            else:
                team_open = "n.v.t."
                aantal_open = 0

            st.markdown(f"""
            ### ℹ️ Conclusie
            - Meeste **afgehandelde** meldingen: `{team_afgehandeld}` ({aantal_afgehandeld})
            - Meeste **openstaande** meldingen: `{team_open}` ({aantal_open})
            """)



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