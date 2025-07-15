import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURATION PAGE ---
st.set_page_config(
    page_title="Pilotage Business",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("# 📊 Pilotage Business – Dashboard Épuré")

# --- CHARGEMENT EXCEL EMBARQUÉ ---
EXCEL_PATH = "Tableau Pilotage Complet.xlsx"  # Assure-toi de l'avoir uploadé à la racine du repo
sheets = pd.read_excel(EXCEL_PATH, sheet_name=None)

# --- NAVIGATION ---
onglets = ["Tableau de Bord"] + list(sheets.keys())
page = st.sidebar.radio("Navigation", onglets)

# --- PAGE PRINCIPALE ---
if page == "Tableau de Bord":
    st.header("Tableau de Bord Principal")
    col1, col2, col3 = st.columns(3)

    if "Calcul Marges" in sheets:
        df_m = sheets["Calcul Marges"].copy()
        # Forcer numérique et éviter les NaN
        for c in ["Prix de vente HT (€)", "Quantité vendue", "Total CA Produit (€)", "Marge nette (€)"]:
            if c in df_m.columns:
                df_m[c] = pd.to_numeric(df_m[c], errors="coerce").fillna(0)

        ca = (df_m["Prix de vente HT (€)"] * df_m["Quantité vendue"]).sum()
        col1.metric("Chiffre d'affaires HT", f"{ca:,.0f} €")

        if "Marge nette (€)" in df_m.columns:
            marge = df_m["Marge nette (€)"].sum()
            col2.metric("Marge nette totale", f"{marge:,.0f} €")
        else:
            col2.metric("Marge nette totale", "–")

        # Graphique d'évolution
        evo = df_m.groupby(df_m.index).sum()["Total CA Produit (€)"]
        col3.line_chart(evo)
    else:
        st.info("Onglet 'Calcul Marges' introuvable.")

    # --- Tu peux ajouter ici d'autres KPI / graphiques globaux ---

# --- PAGES DÉDIÉES À CHAQUE ONGLET ---
else:
    st.header(page)
    df = sheets[page].copy()

    # Détection des colonnes numériques
    num_cols = df.select_dtypes(include=["int64","float64"]).columns.tolist()

    # Formulaire
    with st.form(key=f"form_{page}"):
        st.subheader("Saisie des données")
        inputs = {}
        for col in num_cols:
            default = float(df[col].iloc[0]) if not df[col].isna().all() else 0.0
            inputs[col] = st.number_input(label=col, value=default, step=1.0)
        calc = st.form_submit_button("Calculer")

    if calc:
        st.subheader("Résultats")
        # Exemple de traitement selon le nom de la page
        low = page.lower()
        if "cout de revien" in low or "cout de revient" in low:
            mp = inputs.get("Coût des matières premières (€)", 0)
            mo = inputs.get("Coût de la main-d’œuvre (€)", 0)
            fi = inputs.get("Frais indirects (€)", 0)
            qte = inputs.get("Quantité produite", 1)
            total = mp + mo + fi
            par_unite = total / qte if qte else 0
            st.metric("Coût total", f"{total:,.2f} €")
            st.metric("Coût par unité", f"{par_unite:,.2f} €")
            st.bar_chart(pd.DataFrame({"€":[mp,mo,fi]}, index=["MP","MO","Indirect"]))

        elif "calcul marges" in low:
            pv = inputs.get("Prix de vente HT (€)", 0)
            cr = inputs.get("Coût de revient par unité (€)", 0)
            marge_e = pv - cr
            pct = (marge_e / pv * 100) if pv else 0
            st.metric("Marge par unité", f"{marge_e:,.2f} €")
            st.metric("Marge (%)", f"{pct:.1f} %")
            fig, ax = plt.subplots()
            ax.bar(["Marge","Coût"], [marge_e, cr])
            ax.set_ylabel("€")
            st.pyplot(fig)

        else:
            st.info("Pour cet onglet, les résultats personnalisés seront affichés ici.")
