"""
Module pour la création et la gestion des cartes interactives.
"""

import folium
from streamlit_folium import st_folium


def create_interactive_map(center_lat, center_lon, friends, bars_sorted, radius_km):
    """
    Crée une carte interactive avec les amis, le centre et les bars.

    Args:
        center_lat (float): Latitude du centre
        center_lon (float): Longitude du centre
        friends (list): Liste des amis
        bars_sorted (list): Liste des bars triés par distance
        radius_km (float): Rayon de recherche en km

    Returns:
        folium.Map: Carte interactive
    """
    # Initialiser la carte centrée sur le groupe d'amis
    m = folium.Map(
        location=[center_lat, center_lon], zoom_start=13, tiles="OpenStreetMap"
    )

    # Ajouter le barycentre sur la carte
    folium.Marker(
        [center_lat, center_lon],
        popup=f"🎯 Centre du groupe<br>Barycentre calculé<br>Lat: {center_lat:.4f}<br>Lon: {center_lon:.4f}",
        icon=folium.Icon(color="purple", icon="bullseye"),
    ).add_to(m)

    # Ajouter un cercle pour visualiser le rayon de recherche
    folium.Circle(
        location=[center_lat, center_lon],
        radius=radius_km * 1000,  # Conversion en mètres
        color="purple",
        fill=True,
        fillOpacity=0.1,
        popup=f"Zone de recherche: {radius_km} km",
    ).add_to(m)

    # Ajouter les amis sur la carte
    add_friends_to_map(m, friends)

    # Ajouter les 5 meilleurs bars sur la carte
    add_bars_to_map(m, bars_sorted[:5])

    return m


def add_friends_to_map(map_obj, friends):
    """
    Ajoute les marqueurs des amis sur la carte.

    Args:
        map_obj (folium.Map): Objet carte
        friends (list): Liste des amis
    """
    for friend in friends:
        if friend.get("latitude") and friend.get("longitude"):
            folium.Marker(
                [friend["latitude"], friend["longitude"]],
                popup=f"👤 {friend['name']}<br>{friend['address']}",
                icon=folium.Icon(color="blue", icon="user"),
            ).add_to(map_obj)


def add_bars_to_map(map_obj, bars):
    """
    Ajoute les marqueurs des bars sur la carte.

    Args:
        map_obj (folium.Map): Objet carte
        bars (list): Liste des bars
    """
    for i, bar in enumerate(bars):
        color = "red" if i == 0 else "orange" if i < 3 else "green"
        icon = "star" if i == 0 else "glass"

        folium.Marker(
            [bar["lat"], bar["lon"]],
            popup=f"🍻 {bar['name']}<br>{bar['type']}<br>Distance moyenne: {bar['avg_distance']:.1f} km",
            icon=folium.Icon(color=color, icon=icon),
        ).add_to(map_obj)


def display_map(map_obj):
    """
    Affiche la carte dans Streamlit.

    Args:
        map_obj (folium.Map): Objet carte à afficher

    Returns:
        dict: Données de la carte
    """
    return st_folium(map_obj, width=700, height=500)
