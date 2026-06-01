import streamlit as st
import pandas as pd
import requests

st.title("Extracteur API Sirene - Version Complète")

API_KEY = "6f840b13-7522-4345-840b-1375229345b8"
HEADERS = {
    "X-INSEE-Api-Key-Integration": API_KEY, 
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

uploaded_file = st.file_uploader("Upload votre CSV de SIREN", type="csv")

if uploaded_file:
    df_input = pd.read_csv(uploaded_file)
    
    if st.button("Lancer l'extraction"):
        all_results = []
        progress_bar = st.progress(0)
        
        # On utilise une liste pour collecter toutes les lignes, 
        # même s'il y a plusieurs périodes par SIREN
        for i, siren in enumerate(df_input['SIREN'].astype(str)):
            url = f"https://api.insee.fr/api-sirene/3.11/siren/{siren}"
            try:
                response = requests.get(url, headers=HEADERS, timeout=10)
                if response.status_code == 200:
                    data = response.json().get("uniteLegale", {})
                    periodes = data.get("periodesUniteLegale", [])
                    
                    for p in periodes:
                        # On aplatit les données de la période
                        ligne = {k: v for k, v in p.items() if v is not None}
                        ligne['siren'] = siren
                        all_results.append(ligne)
                else:
                    st.warning(f"SIREN {siren} introuvable (Code {response.status_code})")
            except Exception as e:
                st.error(f"Erreur sur {siren}: {e}")
            
            progress_bar.progress((i + 1) / len(df_input))
        
        # Création du DataFrame final
        final_df = pd.DataFrame(all_results)
        
        st.write(f"Nombre total de lignes extraites : {len(final_df)}")
        st.dataframe(final_df.head(10)) # Aperçu
        
        # Export
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Télécharger le CSV complet", csv, "resultats_complets.csv", "text/csv")
