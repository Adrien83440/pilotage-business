import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuration de base
st.set_page_config(page_title="Pilotage Business", layout="wide")

st.markdown("# 📊 Pilotage Business – Dashboard Épuré")

# -------------------------------------------------------------------
# CHARGEMENT AUTOMATIQUE DE TON EXCEL (plus besoin de l’uploader)
# -------------------------------------------------------------------
EXCEL_PATH = "Tableau Pilotage Complet.xlsx"  # ou "data/Tableau Pilotage Complet.xlsx"
sheets = pd.read_excel(EXCEL_PATH, sheet_name=None)

# On ne montre plus la barre latérale de chargement, juste la nav
onglets = ["Tableau de Bord"] + list(sheets.keys())
page = st.sidebar.radio("Navigation", onglets)

# ... reste du code inchangé, qui utilise directement `sheets`
