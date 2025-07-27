import streamlit as st
from bijlage import kolom_aliases
import pandas as pd

def check_data(df):
    df.columns = df.columns.str.strip()
    df.columns = [kolom_aliases.get(col, col) for col in df.columns]

    vereiste_kolommen = [
        "indexnummer", "klachtnummer", "naam", "email", "telefoon", "datum",
        "hoofdcategorie", "subcategorie", "behandeltermijn", "status", "bron",
        "gebied", "wijk", "tevredenheid", "team", "wijziging", "behandelsduur"
    ]
    if not all(k in df.columns for k in vereiste_kolommen):
        return "error", "Het CSV-bestand mist één of meer verplichte kolommen.", None

    totaal_rijen = df.shape[0]
    aantal_nan_rijen = df[df.isnull().any(axis=1)].shape[0]
    if aantal_nan_rijen / totaal_rijen < 0.5:
        return "error", "Er zijn te veel ontbrekende waarden.", None

    df_schoon = df.dropna(subset=["hoofdcategorie", "subcategorie", "bron"])
    aantal_verwijderd = totaal_rijen - df_schoon.shape[0]
    if aantal_verwijderd > 0:
        return "warning", f"{aantal_verwijderd} rijen met ontbrekende waarden zijn verwijderd.", df_schoon
    return "ok", "CSV is succesvol ingelezen zonder ontbrekende waarden.", df

