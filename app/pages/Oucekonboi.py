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
from src.transit_utils import (
    calculate_weighted_center_by_transit_time,
    calculate_average_transit_time,
)
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
st.subheader("🚇 Calcul du barycentre optimisé par transport")

# Choix du mode de calcul
calc_mode = st.radio(
    "Mode de calcul du barycentre :",
    ["🗺️ Distance géographique", "🚇 Temps de transport en commun"],
    help="Choisissez comment calculer le centre optimal du groupe",
)

if calc_mode == "🚇 Temps de transport en commun":
    with st.spinner(
        "🚇 Calcul du barycentre optimisé par transport (cela peut prendre quelques secondes)..."
    ):
        center_lat, center_lon, transit_times, calc_info = (
            calculate_weighted_center_by_transit_time(friends)
        )

    # Afficher un résumé des résultats d'optimisation
    if calc_info:
        st.subheader("📊 Résumé de l'optimisation")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "⏱️ Temps initial moyen", f"{calc_info['avg_initial_time']:.0f} min"
            )
        with col2:
            st.metric("⏱️ Temps final moyen", f"{calc_info['avg_final_time']:.0f} min")
        with col3:
            improvement = calc_info["time_improvement"]
            emoji = "📈" if improvement > 0 else "📊"
            st.metric(f"{emoji} Amélioration", f"{improvement:+.0f} min")

        st.info(
            f"📏 Le barycentre a été déplacé de **{calc_info['displacement_km']:.0f} mètres** "
            f"pour optimiser les temps de trajet."
        )

        # Afficher les différences de temps individuelles
        st.subheader("⏱️ Comparaison des temps de trajet")
        st.markdown("**Temps vers l'ancien barycentre vs nouveau barycentre :**")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🔴 Ancien barycentre :**")
            for name, old_time in calc_info["initial_times"].items():
                st.write(f"🚇 {name}: {old_time:.0f} min")

        with col2:
            st.markdown("**🟢 Nouveau barycentre :**")
            for name, new_time in transit_times.items():
                old_time = calc_info["initial_times"][name]
                diff = new_time - old_time
                emoji = "✅" if diff <= 0 else "⚠️"
                st.write(f"{emoji} {name}: {new_time:.0f} min ({diff:+.0f})")

    # Stocker les informations pour la carte
    initial_center = calc_info.get("initial_center") if calc_info else None
    use_transit_for_bars = True
else:
    center_lat, center_lon = calculate_center(friends)
    st.success("✅ Barycentre géographique calculé (centre de masse des positions)")
    initial_center = None  # Pas d'ancien centre en mode géographique
    use_transit_for_bars = False

# Afficher les informations du barycentre et obtenir le rayon de recherche
radius_km = display_center_info(center_lat, center_lon)

# Obtenir la liste des bars autour du barycentre
with st.spinner(
    f"🔍 Recherche des bars dans un rayon de {radius_km} km autour du centre du groupe..."
):
    bars = get_bars_around_center(center_lat, center_lon, radius_km=radius_km)

# Afficher les résultats de la recherche
display_search_results(len(bars))

# Calculer la distance/temps moyen pour chaque bar
if use_transit_for_bars:
    with st.spinner("🚇 Calcul des temps de trajet vers les bars..."):
        for bar in bars:
            bar["avg_time"] = calculate_average_transit_time(
                bar["lat"], bar["lon"], friends
            )
            bar["avg_distance"] = bar["avg_time"]  # Pour compatibilité avec l'affichage

    # Trier les bars par temps de trajet moyen
    bars_sorted = sorted(bars, key=lambda x: x["avg_time"])
    metric_unit = "min"
    metric_type = "Temps moyen"
else:
    for bar in bars:
        bar["avg_distance"] = calculate_average_distance(
            bar["lat"], bar["lon"], friends
        )

    # Trier les bars par distance moyenne
    bars_sorted = sorted(bars, key=lambda x: x["avg_distance"])
    metric_unit = "km"
    metric_type = "Distance moyenne"

# Afficher les statistiques
best_bar = bars_sorted[0]
display_statistics(friends, bars, best_bar, metric_type, metric_unit)

# Créer et afficher la carte interactive
st.subheader("🗺️ Carte interactive")
map_obj = create_interactive_map(
    center_lat, center_lon, friends, bars_sorted, radius_km, initial_center
)
map_data = display_map(map_obj)

# Afficher le classement des bars
display_bars_ranking(bars_sorted, metric_type, metric_unit)

# Afficher les détails du meilleur bar
display_best_bar_details(
    best_bar,
    friends,
    center_lat,
    center_lon,
    use_transit_for_bars,
    metric_type,
    metric_unit,
)

# Bouton de rafraîchissement
display_refresh_button()
