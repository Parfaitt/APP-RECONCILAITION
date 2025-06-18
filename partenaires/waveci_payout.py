import pandas as pd
import streamlit as st
import csv
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
from utils.helpers import metric_card

class WaveciPayoutProcessor:
    def __init__(self, data_file, partner_file):
        self.data_file = data_file
        self.partner_file = partner_file
    
    def load_file(self, file):
        # Votre fonction de chargement existante
        try:
            if file.name.endswith(".csv"):
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
    
    def process(self):
        # Charger les données
        pmt = self.load_file(self.data_file)
        dfop = self.load_file(self.partner_file)
        
        # traitement mtnci payin
        
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
        
        # --- Nettoyage & transformation CHEZ LE PARTENAIRE-------------------------------
        def extractdays(dateds):
            parts=dateds.split(' ')
            return parts[0]
        dfop['DateCourte']= dfop['Horodatage'].apply(extractdays)
        
        
        payin= dfop.loc[(dfop['Type de transaction'] == 'api_payout')]

        
         # Calcul des KPI------------------------------------
        
         # Calcul des KPI-----------------------------------------
        
        #MISE EN PLACE DE RECHERCHE X POUR RECUPERATION CHEZ LE PARTENAIRE
        # Supprimer les doublons en conservant la première occurrence
        payin = payin.drop_duplicates(subset='Référence client')
        
        # Vérification des correspondances entre A1 et B1
        #correspondance_statut_op= payin.set_index('Externalid')['Status']
        correspondance_date_op = payin.set_index('Référence client')['DateCourte']
        correspondance_idoperator = payin.set_index('Référence client')['Identifiant de session API']
        
        
        dfpmt['DATEOP'] = dfpmt['Transaction ID'].map(correspondance_date_op)
        #dfpmt['STATUTOP'] = dfpmt['Transaction ID'].map(correspondance_statut_op)
        dfpmt['IDOPERATOR'] = dfpmt['Transaction ID'].map(correspondance_idoperator)
                
        
        # Définir les taux de commission pour chaque opérateur
        dfpmt['Fraisop'] = dfpmt['Montant'] * 0.01
        dfpmt['FraisPmt'] = dfpmt['Fee amount'] - dfpmt['Fraisop']
        dfpmt['Tauxop']=dfpmt['Fraisop'] / dfpmt['Montant']
        payin['Tauxop']=payin['Frais'] / payin['Montant']

        payin['Net']=(payin['Montant'] + payin['Frais'])
        
        #NBSI PMT &CINETPAY
        dfpmt['WAVE'] = dfpmt['Transaction ID'].isin(payin['Référence client']).astype(int)
        payin['PMT'] = payin['Référence client'].isin(dfpmt['Transaction ID']).astype(int)

        dfpmt['Nombre']= dfpmt['Montant']
        payin['Nombre']= payin['Montant']

        # --- Création des onglets ---

        tabs = st.tabs(["📊 Vue Globale", "👥 Rapport Reconciliation", "🔄 Rapport", "📈 Analytics Avancés"])
    
            # ==================================
               # Onglet 1 : Vue Globale
           # ==================================
        with tabs[0]:
            st.subheader("Vue Globale")
            #Sélecteur de période
            montant_total = dfpmt["Montant"].sum()
            nombre_transaction = dfpmt['Transaction ID'].count()
            taux_succes = (dfpmt[dfpmt['Statut'] == 'SUCCESS'].shape[0] / nombre_transaction) * 100
            trx_succes = (dfpmt[dfpmt['Statut'] == 'SUCCESS'])
            select=trx_succes['Transaction ID'].count()

            # Affichage dans des metric cards améliorées
            col1, col2, col3, col4 = st.columns(4)
            col1.markdown(metric_card("Transactions", nombre_transaction, "#1E90FF", "🔄"), unsafe_allow_html=True)
            col2.markdown(metric_card("Transactions Succès", select, "#1E90FF", "🔄"), unsafe_allow_html=True)
            col3.markdown(metric_card("Montant Total", f"{montant_total:,.2f}", "#2E8B57", "💰"), unsafe_allow_html=True)
            col4.markdown(metric_card("Taux de Succès", f"{taux_succes:.1f}%", "#FFA500", "✅"), unsafe_allow_html=True)
            
            # Nouveau: Graphique combiné montant/nombre de transactions
            st.subheader("Évolution Journalière")
            daily_data = dfpmt.groupby('Date').agg(
                Montant=('Montant', 'sum'),
                Transactions=('Transaction ID', 'count')
            ).reset_index()
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                px.line(daily_data, x='Date', y='Montant').data[0],
                secondary_y=False,
            )
            fig.add_trace(
                px.bar(daily_data, x='Date', y='Transactions').data[0],
                secondary_y=True,
            )
            fig.update_layout(
                title="Volume et Nombre de Transactions",
                yaxis_title="Montant (XOF)",
                yaxis2_title="Nombre de Transactions",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        # ================================
    # Onglet 2  : Opérations
# ================================

        with tabs[1]:
            
            st.subheader("Rapport Reconciliation WAVE CI PAYOUT")
            df_filteredpmt = dfpmt[dfpmt['WAVE'] == 1]
            
            # Nouveau: Métriques de réconciliation
            matched = df_filteredpmt['WAVE'].sum()
            unmatched = len(dfpmt) - matched
            reconciliation_rate = (matched / len(dfpmt)) * 100
            maj=df_filteredpmt[(df_filteredpmt['Statut']=='FAILED') | (df_filteredpmt['Statut']=='PENDING')]
            nbre_maj=maj['Transaction ID'].count()
            
            col1, col2, col3,col4 = st.columns(4)
            col2.metric("Transactions Matchées", matched, delta=f"{reconciliation_rate:.1f}%")
            col3.metric("Nombre transaction MAJ", nbre_maj)
            col4.metric("Transactions Non Matchées", unmatched)
            col1.metric("Total Transactions", len(dfpmt))
            # Création du tableau croisé dynamique
            df_filteredpmt = dfpmt[dfpmt['WAVE'] == 1]
        # Création du tableau croisé dynamique
            tcdpmt = pd.pivot_table(
            df_filteredpmt,
            values=['Montant', 'Nombre','Fraisop', 'FraisPmt'],
            index=['DATEOP','Statut'],
            aggfunc={'Nombre': 'count','Montant': 'sum' ,'Fraisop': 'sum', 'FraisPmt': 'sum' },
            fill_value=0,
            margins=True,
            margins_name='Total'
        )
            # Création du tableau croisé dynamique
            df_filtered = payin[(payin['PMT'] == 1) | (payin['PMT'] == 0)]

        # Création du tableau croisé dynamique
            tcdwave = pd.pivot_table(
            df_filtered,
            values=['Nombre', 'Net'],
            index=['DateCourte'],
            aggfunc={'Nombre': 'count','Net': 'sum' },
            fill_value=0,
            margins=True,
            margins_name='Total'
        )
            tab1, tab2, tab3, tab4 = st.tabs(["Données PMT", "Données Partenaire", "TCD PMT", "TCD Partenaire"])
            
            with tab1:
                st.write(dfpmt)
                
            with tab2:
                st.write(payin)
                
            with tab3:
                st.write(tcdpmt)
                
            with tab4:
                st.write(tcdwave)
            
            # LES TRANSACTIONS A METTRE A JOUR
            
            maj_failed_a_succes = dfpmt.loc[(dfpmt['Statut'] == 'FAILED') & (dfpmt['WAVE'] == 1)]
            maj_pending_a_succes = dfpmt.loc[(dfpmt['Statut'] == 'PENDING') & (dfpmt['WAVE'] == 1)]
            trx_succes_abs = dfpmt.loc[(dfpmt['Statut'] == 'SUCCESS') & (dfpmt['WAVE'] == 0)]
            trx_en_attente_abs= dfpmt.loc[(dfpmt['Statut']=='PENDING') & (dfpmt['WAVE'] == 0)]
            trx_succes_cinetpay_abs_pmt = payin.loc[(payin['PMT'] == 0)]
            select_marchand=df_filteredpmt.groupby(['Pays','Merchant Name','Operator']).agg(
                Nombre=('Montant', 'count'),
                Volume_transaction=('Montant','sum')
            )
            
            select_country_marchand_statut = df_filteredpmt.groupby(['Pays']).agg(
                Nombre=('Montant', 'count'),
                Volume=('Montant', 'sum')
            )
            

            refound=dfop[dfop['Type de transaction']=='api_payout_reversal']
            recouvrement=dfop[dfop['Type de transaction']=='agent_transaction']
            
            st.subheader("🔴 Transactions failed à mettre à jour en SUCCESS")
            st.write(maj_failed_a_succes)
            
            st.subheader("🟡 Transactions PENDING à mettre à jour en SUCCESS")
            st.write(maj_pending_a_succes)
            
            st.subheader("🔵 Transactions en attente PMT absentes chez partenaire")
            st.write(trx_en_attente_abs)
            
            st.subheader("🟢 Transactions SUCCES absentes chez partenaire")
            st.write(trx_succes_cinetpay_abs_pmt)
            
            st.subheader("🟠 Transactions SUCCES partenaire absentes PMT")
            st.write(trx_succes_abs)
            
            st.subheader("🟤 TRANSACTION PAR OPERATEUR ET MARCHAND")
            st.write(select_marchand)

            st.subheader("🟩 RETOUR DE FONDS (REFOUND)")
            st.write(refound)
            
            st.subheader("📊🔵 RECOUVREMENT")
            st.write(recouvrement)
            
            st.subheader("🔵 TRANSACTION PAR OPERATEUR ET PAYS")
            st.write(select_country_marchand_statut)
        
        with tabs[2]:
            st.subheader('Vue globale par Statut')
            chart1, chart2= st.columns((2))
            with chart1:
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

        with tabs[3]:
            st.subheader("Analytics Avancés")
            

            # Analyse temporelle avancée
            st.subheader("Analyse Temporelle")
            dfpmt['Date'] = pd.to_datetime(dfpmt['Date'])
            dfpmt['Jour'] = dfpmt['Date'].dt.day_name(locale='fr')
            dfpmt['Heure'] = pd.to_datetime(dfpmt['Created Date']).dt.hour
            
            col1, col2 = st.columns(2)
            with col1:
                day_order = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
                by_day = dfpmt.groupby('Jour').agg({'Montant': 'sum', 'Transaction ID': 'count'}).reindex(day_order)
                fig = px.line(by_day, x=by_day.index, y='Montant', 
                             title="Volume par Jour de la Semaine",
                             labels={'x': 'Jour', 'y': 'Montant'})
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                by_hour = dfpmt.groupby('Heure').agg({'Montant': 'sum', 'Transaction ID': 'count'})
                fig = px.area(by_hour, x=by_hour.index, y='Montant', 
                             title="Volume par Heure de la Journée",
                             labels={'x': 'Heure', 'y': 'Montant'})
                st.plotly_chart(fig, use_container_width=True)
        
        #Processed Cinetpay payin fin-