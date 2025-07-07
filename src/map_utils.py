"""
Module pour la création et la gestion des cartes interactives.
"""

import folium
from streamlit_folium import st_folium


def create_interactive_map(
    center_lat, center_lon, friends, bars_sorted, radius_km, initial_center=None
):
    """
    Crée une carte interactive avec les amis, le centre et les bars.

    Args:
        center_lat (float): Latitude du centre optimisé
        center_lon (float): Longitude du centre optimisé
        friends (list): Liste des amis
        bars_sorted (list): Liste des bars triés par distance
        radius_km (float): Rayon de recherche en km
        initial_center (tuple): (lat, lon) du barycentre initial (optionnel)

    Returns:
        folium.Map: Carte interactive
    """
    # Initialiser la carte centrée sur le groupe d'amis
    m = folium.Map(
        location=[center_lat, center_lon], zoom_start=13, tiles="OpenStreetMap"
    )

    # Ajouter l'ancien barycentre si disponible
    if initial_center:
        initial_lat, initial_lon = initial_center
        folium.Marker(
            [initial_lat, initial_lon],
            popup=f"🔴 Ancien barycentre<br>Centre géographique initial<br>Lat: {initial_lat:.4f}<br>Lon: {initial_lon:.4f}",
            icon=folium.Icon(color="red", icon="times"),
        ).add_to(m)

        # Ajouter une ligne entre l'ancien et le nouveau centre
        folium.PolyLine(
            [(initial_lat, initial_lon), (center_lat, center_lon)],
            color="red",
            weight=3,
            opacity=0.8,
            dash_array="10,5",
            popup="🔄 Optimisation du barycentre",
        ).add_to(m)

    # Ajouter le barycentre optimisé sur la carte
    center_label = "🟢 Barycentre optimisé" if initial_center else "🎯 Centre du groupe"
    folium.Marker(
        [center_lat, center_lon],
        popup=f"{center_label}<br>Barycentre calculé<br>Lat: {center_lat:.4f}<br>Lon: {center_lon:.4f}",
        icon=folium.Icon(
            color="green" if initial_center else "purple", icon="bullseye"
        ),
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
        color = "green" if i == 0 else "lightgreen" if i < 3 else "orange"
        icon = "star" if i == 0 else "glass"

        # Déterminer le métrique à afficher (temps ou distance)
        if "avg_time" in bar and bar["avg_time"] != bar.get("avg_distance", 0):
            metric_info = f"Temps moyen: {bar['avg_time']:.1f} min"
        else:
            metric_info = f"Distance moyenne: {bar['avg_distance']:.1f} km"

        folium.Marker(
            [bar["lat"], bar["lon"]],
            popup=f"🍻 {bar['name']}<br>{bar['type']}<br>{metric_info}",
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
