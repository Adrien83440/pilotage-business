import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuration de la page
st.set_page_config(
    page_title="Pilotage Business",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre de l'application
st.markdown("# 📊 Pilotage Business - Dashboard Épuré")

# Chargement du fichier Excel
uploaded = st.sidebar.file_uploader("Importez votre source de données (.xlsx)", type=["xlsx"])

if uploaded:
    # Lecture de toutes les feuilles
    sheets = pd.read_excel(uploaded, sheet_name=None)
    onglets = ["Tableau de Bord"] + list(sheets.keys())
    page = st.sidebar.radio("Navigation", onglets)

    # -------------------
    # Page principale
    # -------------------
    if page == "Tableau de Bord":
        st.header("Tableau de Bord Principal")
        cols = st.columns(3)

        # KPI & graph si on a la feuille 'Calcul Marges'
        if "Calcul Marges" in sheets:
            df_m = sheets["Calcul Marges"].copy()
            # Forcer numérique
            df_m["Prix de vente HT (€)"] = pd.to_numeric(df_m.get("Prix de vente HT (€)", 0), errors="coerce").fillna(0)
            df_m["Quantité vendue"]      = pd.to_numeric(df_m.get("Quantité vendue", 0), errors="coerce").fillna(0)
            df_m["Total CA Produit (€)"] = pd.to_numeric(df_m.get("Total CA Produit (€)", 0), errors="coerce").fillna(0)

            ca = (df_m["Prix de vente HT (€)"] * df_m["Quantité vendue"]).sum()
            # Si marge nette dispo
            if "Marge nette (€)" in df_m.columns:
                marge = pd.to_numeric(df_m["Marge nette (€)"], errors="coerce").fillna(0).sum()
                cols[1].metric("Marge nette totale", f"{marge:,.0f} €")
            else:
                cols[1].metric("Marge nette totale", "–")

            cols[0].metric("Chiffre d'affaires HT", f"{ca:,.0f} €")

            # Graphique d’évolution du CA
            evo = df_m.groupby(df_m.index).sum()["Total CA Produit (€)"]
            cols[2].line_chart(evo)
        else:
            st.info("Onglet 'Calcul Marges' introuvable.")

        # Ici tu peux ajouter d'autres KPI globaux ou graphiques

    # -------------------
    # Pages par onglet
    # -------------------
    else:
        st.header(page)
        df = sheets[page].copy()

        # On repère les colonnes numériques pour la saisie
        num_cols = df.select_dtypes(include=["int64","float64"]).columns.tolist()

        with st.form(key=f"form_{page}"):
            st.subheader("Saisie des données")
            inputs = {}
            for col in num_cols:
                default = float(df[col].iloc[0]) if not df[col].isna().all() else 0.0
                inputs[col] = st.number_input(label=col, value=default, step=1.0)
            submitted = st.form_submit_button("Calculer")

        if submitted:
            st.subheader("Résultats")

            # Calcul Coût de revient
            if page.lower().startswith("calcul cout"):
                mp = inputs.get("Coût des matières premières (€)", 0)
                mo = inputs.get("Coût de la main-d’œuvre (€)", 0)
                fi = inputs.get("Frais indirects (€)", 0)
                qte = inputs.get("Quantité produite", 1)
                total = mp + mo + fi
                par_unite = total / qte if qte else 0
                st.metric("Coût total", f"{total:,.2f} €")
                st.metric("Coût par unité", f"{par_unite:,.2f} €")
                st.bar_chart(
                    pd.DataFrame({
                        "Montants (€)": [mp, mo, fi]
                    }, index=["MP","MO","Indirect"])
                )

            # Calcul Marges
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

            # Autres onglets : placeholder
            else:
                st.write("Ici, on affichera des métriques et graphiques pour cet onglet.")

else:
    st.warning("Chargez un fichier Excel pour démarrer l'application.")
