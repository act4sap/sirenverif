import streamlit as st
import pandas as pd
import requests

st.title("Extracteur API Sirene INSEE")

# Configuration
API_KEY = "6f840b13-7522-4345-840b-1375229345b8"
HEADERS = {"X-INSEE-Api-Key-Integration": API_KEY, "Accept": "application/json"}

# Upload du fichier
uploaded_file = st.file_uploader("Choisissez votre fichier CSV (colonne 'SIREN')", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if st.button("Lancer l'extraction"):
        results = []
        progress_bar = st.progress(0)
        
        for i, siren in enumerate(df['SIREN']):
            url = f"https://api.insee.fr/api-sirene/3.11/siren/{siren}"
            response = requests.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json().get("uniteLegale", {})
                periodes = data.get("periodesUniteLegale", [])
                
                if periodes:
                    # On ne garde que les champs non nuls de la première période
                    filtre = {k: v for k, v in periodes[0].items() if v is not None}
                    filtre['siren'] = siren
                    results.append(filtre)
            
            progress_bar.progress((i + 1) / len(df))
        
        # Transformation en DataFrame et affichage
        result_df = pd.DataFrame(results)
        st.success("Extraction terminée !")
        st.dataframe(result_df)
        
        # Bouton de téléchargement
        csv = result_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Télécharger le CSV", csv, "resultats.csv", "text/csv")
