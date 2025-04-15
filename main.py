import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="APP Reconciliation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pandas as pd
from styles.custom import load_css
from partenaires import get_processor
from styles import custom
from utils.helpers import metric_card

# Charger les styles CSS
custom.load_css()

# En-tête personnalisé
st.markdown("""
    <div class='banking-header'>
        <h1 style='margin:0; font-weight:700;'>📊 APP RECONCILIATION REVENU ASSURANCE</h1>
        <p style='opacity:0.9; font-weight:300;'>APP de reconciliation RA</p>
    </div>
""", unsafe_allow_html=True)

# Fonction utilitaire pour créer des "metric cards"
def metric_card(title, value, bg_color):
    html = f"""
    <div style="
        background-color: {bg_color};
        padding: 15px;
        border-radius: 8px;
        color: white;
        text-align: center;
        box-shadow: 0 3px 5px rgba(0,0,0,0.1);
        ">
        <h4 style="margin: 0; font-weight: 600; font-size: 1rem;">{title}</h4>
        <p style="font-size: 1.5rem; margin: 5px 0 0; font-weight: bold;">{value}</p>
    </div>
    """
    return html

# Chargement des fichiers
st.sidebar.subheader("1️⃣ Fichier Données PMT")
data_file = st.sidebar.file_uploader("Charger le fichier `PMT` (CSV ou Excel)", type=["csv", "xlsx", "xls"])

st.sidebar.subheader("2️⃣ Fichier Partenaire")
partenaire_file = st.sidebar.file_uploader("Charger le fichier `partenaire` (CSV ou Excel)", type=["csv", "xlsx", "xls"])

if not data_file or not partenaire_file:
    st.warning("Veuillez charger les deux fichiers pour continuer")
    st.stop()

# Détection du partenaire et traitement
try:
    processor = get_processor(partenaire_file.name, data_file, partenaire_file)
    results = processor.process()
    
    # Affichage des résultats
    
    
except Exception as e:
    st.error(f"Erreur de traitement: {str(e)}")