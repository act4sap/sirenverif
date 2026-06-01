import streamlit as st
import pandas as pd
import requests
import time

# Configuration de la page
st.set_page_config(page_title="Extracteur SIRENE", layout="wide")
st.title("🚀 Extracteur API Sirene INSEE")

# Configuration API
API_KEY = "6f840b13-7522-4345-840b-1375229345b8"
HEADERS = {
    "X-INSEE-Api-Key-Integration": API_KEY, 
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; SirenExtractor/1.0)"
}

uploaded_file = st.file_uploader("Déposez votre fichier CSV (colonne 'SIREN')", type="csv")

if uploaded_file:
    df_input = pd.read_csv(uploaded_file, dtype={'SIREN': str}) # Force le type string pour les SIREN
    
    if 'SIREN' not in df_input.columns:
        st.error("Le fichier doit contenir une colonne nommée 'SIREN'")
    else:
        if st.button("Lancer l'extraction"):
            all_results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            siren_list = df_input['SIREN'].dropna().unique()
            
            for i, siren in enumerate(siren_list):
                url = f"https://api.insee.fr/api-sirene/3.11/siren/{siren}"
                
                # Temporisation pour éviter l'erreur 429
                time.sleep(0.6) 
                
                try:
                    response = requests.get(url, headers=HEADERS, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json().get("uniteLegale", {})
                        periodes = data.get("periodesUniteLegale", [])
                        
                        for p in periodes:
                            # Extraction des champs non nuls
                            ligne = {k: v for k, v in p.items() if v is not None}
                            ligne['siren_input'] = siren
                            all_results.append(ligne)
                            
                    elif response.status_code == 429:
                        status_text.warning(f"Pause de sécurité (429) pour le SIREN {siren}...")
                        time.sleep(10) # Pause longue en cas de saturation
                    else:
                        st.write(f"SIREN {siren} non trouvé ou erreur {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Erreur réseau sur {siren}: {e}")
                
                progress_bar.progress((i + 1) / len(siren_list))
                status_text.text(f"Traitement : {i + 1} / {len(siren_list)} SIRENs")

            # Finalisation
            if all_results:
                final_df = pd.DataFrame(all_results)
                st.success(f"Extraction terminée ! {len(final_df)} lignes générées.")
                st.dataframe(final_df.head(20))
                
                csv = final_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button("Télécharger le CSV complet", csv, "resultats_insee.csv", "text/csv")
            else:
                st.error("Aucune donnée récupérée.")
