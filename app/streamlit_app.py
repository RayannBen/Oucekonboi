import streamlit as st
import pandas as pd
import json
import os

# Configuration de la page
st.set_page_config(
    page_title="Oucekonboi - Trouveur de bars", page_icon="🍻", layout="wide"
)

# Titre principal
st.title("🍻 Oucekonboi - Trouveur de bars")
st.markdown("### Trouvez le bar parfait le plus proche de tous vos amis !")

# Créer le dossier data s'il n'existe pas
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Instructions
st.markdown(
    """
👈 **Utilisez le menu de navigation à gauche pour :**
- **Les Copaines** : Inscrire vos amis et leurs adresses
- **Oucekonboi** : Voir les bars recommandés à Paris

L'application calcule automatiquement le meilleur bar en fonction de la localisation de tous vos amis !
"""
)
