import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuration de la page
st.set_page_config(page_title="Pilotage Business", layout="wide", initial_sidebar_state="expanded")

# Titre de l'application
st.markdown("# 📊 Pilotage Business - Dashboard Épuré")

# Chargement du fichier Excel
uploaded = st.sidebar.file_uploader("Importez votre source de données (.xlsx)", type=["xlsx"])

if uploaded:
    # Lecture de toutes les feuilles
    sheets = pd.read_excel(uploaded, sheet_name=None)
    onglets = ["Tableau de Bord"] + list(sheets.keys())
    page = st.sidebar.radio("Navigation", onglets)

    # Page principale : Dashboard
    if page == "Tableau de Bord":
        st.header("Tableau de Bord Principal")
        cols = st.columns(3)
        if "Calcul Marges" in sheets:
            df_m = sheets["Calcul Marges"]
            ca = (df_m["Prix de vente HT (€)"] * df_m["Quantité vendue"]).sum()
            marge = df_m["Marge nette (€)"].sum()
            cols[0].metric("Chiffre d'affaires HT", f"{ca:,.0f} €")
            cols[1].metric("Marge nette totale", f"{marge:,.0f} €")
            evolution = df_m.groupby(df_m.index).sum()["Total CA Produit (€)"]
            cols[2].line_chart(evolution)
        else:
            st.info("Onglet 'Calcul Marges' introuvable.")

    # Pages dédiées à chaque onglet
    else:
        st.header(page)
        df = sheets[page]

        # Formulaire de saisie simplifié
        with st.form(key=f"form_{page}"):
            st.subheader("Saisie des données")
            inputs = {}
            for col in df.select_dtypes(include=["int64","float64"]).columns:
                # prend la première valeur comme valeur par défaut
                inputs[col] = st.number_input(label=col, value=float(df[col].iloc[0]), step=1.0)
            submitted = st.form_submit_button("Calculer")

        if submitted:
            st.subheader("Résultats")
            # Exemples de calculs selon la feuille
            if page.lower().startswith("calcul cout"):
                cout_mp = inputs.get("Coût des matières premières (€)", 0)
                cout_mo = inputs.get("Coût de la main-d’œuvre (€)", 0)
                frais_ind = inputs.get("Frais indirects (€)", 0)
                qte = inputs.get("Quantité produite", 1)
                total = cout_mp + cout_mo + frais_ind
                par_unite = total / qte
                st.metric("Coût total", f"{total:,.2f} €")
                st.metric("Coût par unité", f"{par_unite:,.2f} €")
                st.bar_chart([cout_mp, cout_mo, frais_ind], x=["MP","MO","Indirect"])

            elif page.lower().startswith("calcul marges"):
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
                st.write("Ici, on affichera des graphiques et métriques pour cette feuille.")

else:
    st.warning("Chargez un fichier Excel pour démarrer.")
