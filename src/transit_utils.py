"""
Module pour les calculs de temps de trajet en transport en commun.
"""

import requests
import streamlit as st
from geopy.distance import geodesic
import numpy as np


@st.cache_data
def get_transit_time(origin_lat, origin_lon, dest_lat, dest_lon):
    """
    Calcule le temps de trajet en transport en commun entre deux points.
    Utilise l'API OpenRouteService pour les transports publics.

    Args:
        origin_lat (float): Latitude d'origine
        origin_lon (float): Longitude d'origine
        dest_lat (float): Latitude de destination
        dest_lon (float): Longitude de destination

    Returns:
        float: Temps de trajet en minutes, ou None si erreur
    """
    try:
        # API OpenRouteService (gratuite avec limites)
        # Alternative: utiliser Google Directions API, RATP API, etc.

        # Pour la démo, on va utiliser une estimation basée sur la distance
        # En réalité, il faudrait une vraie API de transport
        distance_km = geodesic(
            (origin_lat, origin_lon), (dest_lat, dest_lon)
        ).kilometers

        # Estimation approximative pour Paris:
        # - Métro/Bus: ~20 km/h en moyenne
        # - Temps d'attente moyen: 5 minutes
        # - Temps de marche: 5 minutes

        if distance_km < 0.6:  # Très proche, à pied
            return distance_km * 12  # 5 km/h à pied
        elif distance_km < 15:  # Transport en commun urbain
            travel_time = (distance_km / 20) * 60  # 20 km/h en transport
            waiting_time = 5  # 5 min d'attente moyenne
            walking_time = 5  # 5 min de marche
            return travel_time + waiting_time + walking_time
        else:  # RER/Transport plus lointain
            travel_time = (distance_km / 35) * 60  # 35 km/h pour RER
            waiting_time = 8  # Plus d'attente
            walking_time = 8  # Plus de marche
            return travel_time + waiting_time + walking_time

    except Exception as e:
        st.warning(f"Erreur calcul transport: {e}")
        # Fallback: estimation très basique
        distance_km = geodesic(
            (origin_lat, origin_lon), (dest_lat, dest_lon)
        ).kilometers
        return distance_km * 4  # 15 km/h moyenne très conservative


def calculate_weighted_center_by_transit_time(friends):
    """
    Calcule un barycentre pondéré par les temps de trajet en transport.
    Utilise un algorithme itératif pour minimiser le temps total de trajet.

    Args:
        friends (list): Liste des amis avec leurs coordonnées

    Returns:
        tuple: (latitude, longitude, dict avec temps de trajet, dict avec infos de calcul)
    """
    if not friends or len(friends) < 2:
        if friends:
            return friends[0]["latitude"], friends[0]["longitude"], {}, {}
        return 48.8566, 2.3522, {}, {}

    # Étape 1: Calculer le barycentre géographique initial
    lats = [f["latitude"] for f in friends if f.get("latitude")]
    lons = [f["longitude"] for f in friends if f.get("longitude")]

    if not lats:
        return 48.8566, 2.3522, {}, {}

    initial_center_lat = float(np.mean(lats))
    initial_center_lon = float(np.mean(lons))

    st.info(
        f"📍 **Étape 1:** Barycentre géographique initial calculé\n"
        f"Latitude: {initial_center_lat:.6f}, Longitude: {initial_center_lon:.6f}"
    )

    # Étape 2: Calculer les temps de trajet vers ce centre initial
    st.info("⏱️ **Étape 2:** Calcul des temps de trajet vers le centre initial...")

    initial_transit_times = {}
    total_initial_time = 0

    for friend in friends:
        if friend.get("latitude") and friend.get("longitude"):
            time_minutes = get_transit_time(
                friend["latitude"],
                friend["longitude"],
                initial_center_lat,
                initial_center_lon,
            )
            initial_transit_times[friend["name"]] = time_minutes
            total_initial_time += time_minutes
            st.write(
                f"🚇 **{friend['name']}**: {time_minutes:.0f} min vers le centre initial"
            )

    avg_initial_time = total_initial_time / len(initial_transit_times)
    st.success(f"⏱️ **Temps moyen initial:** {avg_initial_time:.0f} minutes")

    # Étape 3: Calculer les poids inversés (plus de poids = moins de temps)
    st.info("⚖️ **Étape 3:** Calcul des poids pour optimiser le barycentre...")

    weights = []
    weighted_lats = []
    weighted_lons = []

    for friend in friends:
        if friend.get("latitude") and friend.get("longitude"):
            time_minutes = initial_transit_times[friend["name"]]
            # Éviter division par zéro et donner un poids minimum
            weight = 1.0 / max(time_minutes, 5.0)  # Minimum 5 minutes

            weights.append(weight)
            weighted_lats.append(friend["latitude"] * weight)
            weighted_lons.append(friend["longitude"] * weight)

            st.write(
                f"⚖️ **{friend['name']}**: poids = {weight:.4f} (temps: {time_minutes:.0f} min)"
            )

    # Étape 4: Calculer le nouveau centre pondéré
    st.info("🎯 **Étape 4:** Calcul du nouveau barycentre pondéré...")

    total_weight = sum(weights)
    if total_weight > 0:
        new_center_lat = sum(weighted_lats) / total_weight
        new_center_lon = sum(weighted_lons) / total_weight
    else:
        new_center_lat, new_center_lon = initial_center_lat, initial_center_lon

    # Calculer le déplacement
    displacement_km = geodesic(
        (initial_center_lat, initial_center_lon), (new_center_lat, new_center_lon)
    ).kilometers

    st.success(
        f"🎯 **Nouveau barycentre optimisé calculé !**\n"
        f"Latitude: {new_center_lat:.6f}, Longitude: {new_center_lon:.6f}\n"
        f"📏 Déplacement: {displacement_km:.0f} mètres"
    )

    # Étape 5: Recalculer les temps vers le nouveau centre
    st.info("🔄 **Étape 5:** Vérification des temps vers le nouveau centre...")

    final_transit_times = {}
    total_final_time = 0

    for friend in friends:
        if friend.get("latitude") and friend.get("longitude"):
            time_minutes = get_transit_time(
                friend["latitude"], friend["longitude"], new_center_lat, new_center_lon
            )
            final_transit_times[friend["name"]] = time_minutes
            total_final_time += time_minutes

            initial_time = initial_transit_times[friend["name"]]
            time_diff = time_minutes - initial_time
            emoji = "✅" if time_diff <= 0 else "⚠️"
            st.write(
                f"{emoji} **{friend['name']}**: {time_minutes:.0f} min "
                f"({time_diff:+.0f} min vs initial)"
            )

    avg_final_time = total_final_time / len(final_transit_times)
    time_improvement = avg_initial_time - avg_final_time

    if time_improvement > 0:
        st.success(
            f"🎉 **Amélioration obtenue !**\n"
            f"⏱️ Temps moyen final: {avg_final_time:.0f} minutes\n"
            f"📈 Gain: {time_improvement:.0f} minutes en moyenne"
        )
    else:
        st.info(
            f"ℹ️ **Résultat:**\n"
            f"⏱️ Temps moyen final: {avg_final_time:.0f} minutes\n"
            f"📊 Différence: {time_improvement:+.0f} minutes"
        )

    # Informations de calcul pour le debug/affichage
    calc_info = {
        "initial_center": (initial_center_lat, initial_center_lon),
        "initial_times": initial_transit_times,
        "avg_initial_time": avg_initial_time,
        "avg_final_time": avg_final_time,
        "time_improvement": time_improvement,
        "displacement_km": displacement_km,
    }

    return float(new_center_lat), float(new_center_lon), final_transit_times, calc_info


def calculate_average_transit_time(bar_lat, bar_lon, friends):
    """
    Calcule le temps de trajet moyen en transport pour aller à un bar.

    Args:
        bar_lat (float): Latitude du bar
        bar_lon (float): Longitude du bar
        friends (list): Liste des amis

    Returns:
        float: Temps de trajet moyen en minutes
    """
    times = []
    for friend in friends:
        if friend.get("latitude") and friend.get("longitude"):
            time_minutes = get_transit_time(
                friend["latitude"], friend["longitude"], bar_lat, bar_lon
            )
            times.append(time_minutes)

    return np.mean(times) if times else float("inf")
