import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r'C:\Users\oknaa\PycharmProjects\pythonProject2\.venv\Dashboard\klachten.csv')

# print(df.isnull().sum())
df_filtered = df.copy()
df_filtered["tevreden"] = df_filtered["tevredenheid"].fillna("Onbekend")
df_counts = df_filtered.groupby(["team", "tevreden"]).size()


wijzigingswaarden = df["wijziging"].dropna().astype(int)

aantallen = wijzigingswaarden.value_counts().sort_index()

labels = ["In één keer goed" if i == 1 else
          "In twee keer goed" if i == 2 else
          "In drie keer goed" if i == 3 else
          f"In {i} keer goed"
          for i in aantallen.index]
# print(aantallen)
for i in aantallen:
    print(i)
