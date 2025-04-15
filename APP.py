import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
from itertools import combinations
from collections import Counter
import zipfile
import io
import os
from streamlit_extras.stylable_container import stylable_container
import plotly.figure_factory as ff
import csv


# --- Configuration de la page --------------------------------------------
st.set_page_config(
    page_title="APP Reconciliation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
# --- Configuration de la page --------------------------------------------------

# --- Injection CSS---------------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&display=swap');
        * { font-family: 'Inter', sans-serif; box-sizing: border-box; }
        .main { background: #f4f6f8; color: #333; }
        
        /* Sidebar avec un nouveau dégradé (violet et rose) */
        .stSidebar { 
            background: linear-gradient(135deg, #023e8a, #03045e); 
            color: white; 
            padding: 1rem; 
        }
        
        /* Header avec un nouveau dégradé (orange et rouge) */
        .banking-header {
            background: linear-gradient(135deg, #03045e 0%, #023e8a 100%);
            padding: 2.5rem; 
            border-radius: 15px; /* Coins plus arrondis */
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); /* Ombre plus prononcée */
        }
        
        /* Style pour les graphiques Plotly */
        .stPlotlyChart { 
            border: none; 
            border-radius: 15px; /* Coins arrondis pour les graphiques */
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
        }
        
        /* Style pour les DataFrames */
        .dataframe { 
            border-radius: 15px !important; 
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
        }
        
        /* Style pour les boutons et autres éléments interactifs */
        .stButton>button {
            border-radius: 8px;
            background-color: #FF6F61;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            font-size: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .stButton>button:hover {
            background-color: #FF3B3F;
        }
    </style>
""", unsafe_allow_html=True)
# --- Injection CSS---------------------------------------------------------------

# --- En-tête personnalisé ------------------------------------------------------
st.markdown("""
    <div class='banking-header'>
        <h1 style='margin:0; font-weight:700;'>📊 APP RECONCILIATION REVENU ASSURANCE</h1>
        <p style='opacity:0.9; font-weight:300;'>APP de reconciliation RA</p>
    </div>
""", unsafe_allow_html=True)
# --- En-tête personnalisé ------------------------------------------------------

# --- Fonction utilitaire pour créer des "metric cards" compactes ---
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
# --- Fonction utilitaire pour créer des "metric cards" compactes ---
pd.options.display.float_format = '{:.2f}'.format

# Chargement du fichier----------------------------------------

st.sidebar.subheader("1️⃣ Fichier Données PMT")
data_file = st.sidebar.file_uploader("Charger le fichier `PMT` (CSV ou Excel)", type=["csv", "xlsx", "xls"])

# --- Upload fichier "partenaire" ---
st.sidebar.subheader("2️⃣ Fichier Partenaire")
partenaire_file = st.sidebar.file_uploader("Charger le fichier `partenaire` (CSV ou Excel)", type=["csv", "xlsx", "xls"])

# --- Fonction de chargement intelligent ---
def load_file(file):
    try:
        if file.name.endswith(".csv"):
            # Détection automatique du délimiteur pour CSV
            raw_data = file.read().decode("utf-8", errors="ignore")
            dialect = csv.Sniffer().sniff(raw_data.split("\n")[0])
            delimiter = dialect.delimiter
            file.seek(0)
            return pd.read_csv(file, delimiter=delimiter, encoding="utf-8")
        elif file.name.endswith((".xlsx", ".xls")):
            return pd.read_excel(file)
        else:
            st.error("Format non supporté.")
            return None
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        return None

# --- Chargement des fichiers ---
if data_file:
    pmt = load_file(data_file)
    st.success("✅ Fichier `Paymetrust` chargé avec succès.")
else:
    st.warning("Veuillez charger le fichier `PMT` pour continuer.")
    st.stop()

if partenaire_file:
    dfop = load_file(partenaire_file)
    st.success("✅ Fichier `partenaire` chargé avec succès.")
else:
    st.warning("Veuillez charger le fichier `partenaire` pour continuer.")
    st.stop()

# --- Chargement des fichiers -------------------------------------

#Processed Cinetpay payin debut

# --- Nettoyage & transformation PMT-------------------------------
def extractday(dated):
    parts=dated.split(' ')
    return parts[0]
pmt['Date']= pmt['created_at'].apply(extractday)

pmt["amount"] = pd.to_numeric(pmt["amount"], errors="coerce")
pmt = pmt.drop_duplicates(subset='transaction_id', keep='first')
dfpmt = pmt.rename(columns={
        'created_at': 'Created Date',
        'payment_date': 'Payment Date',
        'operator': 'Operator',
        'merchant_name': 'Merchant Name',
        'transaction_id': 'Transaction ID',
        'id_operator': 'ID Opérateur',
        'phone_number': 'Phone Number',
        'amount': 'Montant',
        'country':'Pays',
        'fee_amount': 'Fee amount',
        'merchant_amount': 'Merchant amount',
        'statut': 'Statut'
    })

dfpmt['Phone Number'] = dfpmt['Phone Number'].astype(object)
dfop['Date'] = dfop['Date Creation'].apply(lambda x: x.split(' ')[0])
refused = dfop.loc[(dfop['Statut'] == 'REFUSED')]
dfcinetpay= dfop.loc[(dfop['Statut'] == 'ACCEPTED')]
# --- Nettoyage & transformation CHEZ LE PARTENAIRE-------------------------------

 # Calcul des KPI------------------------------------
st.subheader("Vue Globale")
montant_total = dfpmt["Montant"].sum()
nombre_transaction=dfpmt['Transaction ID'].count()

# Affichage des metric cards
col1, col2= st.columns(2)
col1.markdown(metric_card("Nombre Total Transaction", nombre_transaction, "#1E90FF"), unsafe_allow_html=True)
col2.markdown(metric_card("Montant Total", f"{montant_total:,.2f} XOF", "#2E8B57"), unsafe_allow_html=True)
 # Calcul des KPI-----------------------------------------

#MISE EN PLACE DE RECHERCHE X POUR RECUPERATION CHEZ LE PARTENAIRE

correspondance_statut_op= dfop.set_index('ID transaction')['Statut']
correspondance_statut_refused= refused.set_index('ID transaction')['Statut']
correspondance_date_op = dfop.set_index('ID transaction')['Date']
correspondance_id_op = dfop.set_index('ID transaction')['ID Operator']
correspondance_statut_pmt = dfpmt.set_index('Transaction ID')['Statut']
correspondance_commentaire = refused.set_index('ID transaction')['Commentaire']
correspondance_operator = dfop.set_index('ID transaction')['Opérateur']

dfpmt['DATE_OP'] = dfpmt['Transaction ID'].map(correspondance_date_op)
refused['STATUT_PMT'] = refused['ID transaction'].map(correspondance_statut_pmt)
dfpmt['STATUT_OP'] = dfpmt['Transaction ID'].map(correspondance_statut_op)
dfpmt['REFUSED'] = dfpmt['Transaction ID'].map(correspondance_statut_refused)
dfpmt['ID_OP'] = dfpmt['Transaction ID'].map(correspondance_id_op)
dfpmt['Comment'] = dfpmt['Transaction ID'].map(correspondance_commentaire)
dfpmt['OPERATOROP'] = dfpmt['Transaction ID'].map(correspondance_operator)


# Définir les taux de commission pour chaque opérateur
commission_rates = {
    'TMONEYTG': 0.03,
    'MOOVML': 0.025,
    'FLOOZTG': 0.025,
    'MOOVBF': 0.03,
    'FLOOZ' : 0.003,
    'OMCM': 0.025,
    'MTNGN':0.025,
    'MTNCM':0.025,
    'AIRTELCD':0.035,
    'OMGN' :0.035,
    'MPESACD' :0.038,
    'OMML':0.03,
    'MTNBJ':0.027,
    'WAVECI':0.03,
    'OM':0.03,
    'MOMO':0.03
}

# Fonction pour calculer les frais d'opérateur
def calculate_frais_op(row):
    operator = row['OPERATOROP']
    montant = row['Montant']
    commission_rate = commission_rates.get(operator, 0)
    return montant * commission_rate

# Ajouter une colonne 'frais_op' avec les frais d'opérateur calculés
dfpmt['frais_op'] = dfpmt.apply(calculate_frais_op, axis=1)
dfpmt['Frais_pmt'] = dfpmt['Fee amount'] - dfpmt['frais_op']
dfpmt['Tauxop']=dfpmt['frais_op'] / dfpmt['Montant']
dfop['Taux(%)'] = dfop['Commission'] / dfop['Montant Payé']
dfpmt['Taux_merchant']=dfpmt['Fee amount'] / dfpmt['Montant']
dfpmt['Nombre']= dfpmt['Montant']
dfcinetpay['Nombre']=dfcinetpay['Montant Payé']

#NBSI PMT &CINETPAY
dfpmt['CINETPAY'] = dfpmt['Transaction ID'].isin(dfcinetpay['ID transaction']).astype(int)
dfcinetpay['PMT'] = dfcinetpay['ID transaction'].isin(dfpmt['Transaction ID']).astype(int)
dfpmt['REFUSED'] = dfpmt['Transaction ID'].isin(refused['ID transaction']).astype(int)

df_filtered = dfcinetpay[(dfcinetpay['PMT'] == 1) | (dfcinetpay['PMT'] == 0)]

# Création du tableau croisé dynamique
tcdcinetpay = pd.pivot_table(
    df_filtered,
    values=['Montant Payé', 'Nombre'],
    index=['Date', 'Opérateur','Statut'],
    aggfunc={'Nombre': 'count','Montant Payé': 'sum' },
    fill_value=0,
    margins=True,
    margins_name='Total'
)

df_filteredpmt = dfpmt[dfpmt['CINETPAY'] == 1]

# Création du tableau croisé dynamique
tcdpmt = pd.pivot_table(
    df_filteredpmt,
    values=['Montant', 'Nombre','frais_op', 'Frais_pmt'],
    index=['DATE_OP','OPERATOROP','Statut'],
    aggfunc={'Nombre': 'count','Montant': 'sum' ,'frais_op': 'sum', 'Frais_pmt': 'sum' },
    fill_value=0,
    margins=True,
    margins_name='Total'
)

st.subheader("DONNEES PMT")
st.write(dfpmt)
st.subheader("DONNEES PARTENAIRE")
st.write(dfcinetpay)
st.subheader("TCD PMT")
st.write(tcdpmt)
st.subheader("TCD PARTENAIRE")
st.write(tcdcinetpay)
# LES TRANSACTIONS A METTRE A JOUR

maj_failed_a_succes = dfpmt.loc[(dfpmt['Statut'] == 'FAILED') & (dfpmt['CINETPAY'] == 1)]
maj_pending_a_succes = dfpmt.loc[(dfpmt['Statut'] == 'PENDING') & (dfpmt['CINETPAY'] == 1)]
majf=maj_failed_a_succes[['Transaction ID','Phone Number','Statut','STATUT_OP','ID_OP']]
majp=maj_pending_a_succes[['Transaction ID','Phone Number','Statut','STATUT_OP','ID_OP']]
trx_succes_abs = dfpmt.loc[(dfpmt['Statut'] == 'SUCCESS') & (dfpmt['CINETPAY'] == 0)]
trx_en_attente_abs= dfpmt.loc[(dfpmt['Statut']=='PENDING') & (dfpmt['CINETPAY'] == 0)]
trx_succes_cinetpay_abs_pmt = dfcinetpay.loc[(dfcinetpay['Statut']=='ACCEPTED') & (dfcinetpay['PMT'] == 0)]
select_marchand=df_filteredpmt.groupby(['Pays','Merchant Name','Operator']).agg(
    Nombre=('Montant', 'count'),
    Volume_transaction=('Montant','sum')
)

select_country_marchand_statut = df_filteredpmt.groupby(['Pays']).agg(
    Nombre=('Montant', 'count'),
    Volume=('Montant', 'sum')
)
st.subheader("TRANSACTION FAILED A MAJ EN SUCCES")
st.write(majf)

st.subheader("TRANSACTION PENDING A MAJ EN SUCCES")
st.write(majp)

st.subheader("TRANSACTION EN ATTENTE PMT ABS PARTENAIRE")
st.write(trx_en_attente_abs)

st.subheader("TRANSACTION SUCCES PARTENAIRE ABS PMT")
st.write(trx_succes_cinetpay_abs_pmt)

st.subheader("TRANSACTION SUCCES PMT ABS PARTENAIRE")
st.write(trx_succes_abs)

st.subheader("TRANSACTION PAR OPERATOEUR ET MARCHAND")
st.write(select_marchand)

st.subheader("TRANSACTION PAR OPERATOEUR ET PAYS")
st.write(select_country_marchand_statut)


chart1, chart2= st.columns((2))
with chart1:
    st.subheader('Vue globale par Statut')
    fig=px.pie(dfpmt, values="Montant",names="Statut", template="plotly_dark")
    fig.update_traces(text=dfpmt["Statut"], textposition="inside")
    st.plotly_chart(fig,use_container_width=True)
    
with chart2:
    st.subheader('Vue globale par Pays')
    monthly_statut = dfpmt.groupby("Pays")["Montant"].sum().reset_index()
    fig_month = px.bar(monthly_statut, x="Pays", y="Montant",
    text_auto=True,
    color="Montant",
    color_continuous_scale=["#1E90FF", "#4682B4"],
    template="plotly_white")
    fig_month.update_layout(height=330, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_month, use_container_width=True, config={"displayModeBar": False})

#Processed Cinetpay payin fin-



#Processed BIZAO payin debut

