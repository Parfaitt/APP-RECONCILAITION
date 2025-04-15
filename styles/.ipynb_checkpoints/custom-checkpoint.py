import streamlit as st

def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&display=swap');
        * { font-family: 'Inter', sans-serif; box-sizing: border-box; }
        .main { background: #f4f6f8; color: #333; }
        
        .stSidebar { 
            background: linear-gradient(135deg, #023e8a, #03045e); 
            color: white; 
            padding: 1rem; 
        }
        
        .banking-header {
            background: linear-gradient(135deg, #03045e 0%, #023e8a 100%);
            padding: 2.5rem; 
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .stPlotlyChart { 
            border: none; 
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
        }
        
        .dataframe { 
            border-radius: 15px !important; 
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
        }
        
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