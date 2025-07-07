"""
Page principale Oucekonboi - Trouveur de bars
Application modulaire utilisant les modules du dossier src/
"""

import streamlit as st
import sys
import os

# Ajouter le dossier src au path Python
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data_manager import load_friends
from src.geo_utils import calculate_center, calculate_average_distance
from src.bar_finder import get_bars_around_center
from src.map_utils import create_interactive_map, display_map
from src.ui_components import (
    display_header,
    display_no_friends_warning,
    display_center_info,
    display_search_results,
    display_statistics,
    display_bars_ranking,
    display_best_bar_details,
    display_refresh_button,
)

# Configuration de la page
st.set_page_config(
    page_title="Oucekonboi - Trouveur de bars", page_icon="🍻", layout="wide"
)

# Affichage de l'en-tête
display_header()

# Charger les amis
friends = load_friends()

# Vérifier si des amis sont enregistrés
if not friends:
    display_no_friends_warning()

# Calculer le centre géographique des amis (barycentre)
center_lat, center_lon = calculate_center(friends)

# Afficher les informations du barycentre et obtenir le rayon de recherche
radius_km = display_center_info(center_lat, center_lon)

# Obtenir la liste des bars autour du barycentre
with st.spinner(
    f"🔍 Recherche des bars dans un rayon de {radius_km} km autour du centre du groupe..."
):
    bars = get_bars_around_center(center_lat, center_lon, radius_km=radius_km)

# Afficher les résultats de la recherche
display_search_results(len(bars))

# Calculer la distance moyenne pour chaque bar
for bar in bars:
    bar["avg_distance"] = calculate_average_distance(bar["lat"], bar["lon"], friends)

# Trier les bars par distance moyenne
bars_sorted = sorted(bars, key=lambda x: x["avg_distance"])

# Afficher les statistiques
best_bar = bars_sorted[0]
display_statistics(friends, bars, best_bar)

# Créer et afficher la carte interactive
st.subheader("🗺️ Carte interactive")
map_obj = create_interactive_map(
    center_lat, center_lon, friends, bars_sorted, radius_km
)
map_data = display_map(map_obj)

# Afficher le classement des bars
display_bars_ranking(bars_sorted)

# Afficher les détails du meilleur bar
display_best_bar_details(best_bar, friends, center_lat, center_lon)

# Bouton de rafraîchissement
display_refresh_button()
