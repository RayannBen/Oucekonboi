import streamlit as st
import pandas as pd
import json
import os
import folium
from streamlit_folium import st_folium
import requests
from geopy.distance import geodesic
import numpy as np

st.title("🍻 Oucekonboi - Trouveur de bars")
st.markdown("### Découvrez les meilleurs bars à Paris proches de vos amis")

# Fichier pour stocker les données des amis
DATA_FILE = "data/friends.json"


# Fonction pour charger les données des amis
def load_friends():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# Fonction pour calculer le centre géographique
def calculate_center(friends):
    if not friends:
        return 48.8566, 2.3522  # Centre de Paris par défaut

    lats = [f["latitude"] for f in friends if f.get("latitude")]
    lons = [f["longitude"] for f in friends if f.get("longitude")]

    if not lats:
        return 48.8566, 2.3522

    return float(np.mean(lats)), float(np.mean(lons))


# Fonction pour calculer la distance moyenne depuis un point
def calculate_average_distance(bar_lat, bar_lon, friends):
    distances = []
    for friend in friends:
        if friend.get("latitude") and friend.get("longitude"):
            distance = geodesic(
                (bar_lat, bar_lon), (friend["latitude"], friend["longitude"])
            ).kilometers
            distances.append(distance)

    return np.mean(distances) if distances else float("inf")


# Fonction pour rechercher des bars autour du barycentre via Overpass API
@st.cache_data
def get_bars_around_center(center_lat, center_lon, radius_km: float = 2.0):
    """
    Recherche des bars autour du centre géographique du groupe d'amis
    en utilisant l'API Overpass d'OpenStreetMap
    """
    try:
        # Convertir le rayon en degrés (approximatif)
        radius_deg = radius_km / 111.0  # 1 degré ≈ 111 km

        # Requête Overpass pour trouver les bars
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="bar"]({center_lat-radius_deg},{center_lon-radius_deg},{center_lat+radius_deg},{center_lon+radius_deg});
          node["amenity"="pub"]({center_lat-radius_deg},{center_lon-radius_deg},{center_lat+radius_deg},{center_lon+radius_deg});
        );
        out geom;
        """

        response = requests.get(
            overpass_url, params={"data": overpass_query}, timeout=30
        )
        data = response.json()

        bars = []
        for element in data.get("elements", []):
            if "tags" in element and "name" in element["tags"]:
                name = element["tags"]["name"]
                lat = element["lat"]
                lon = element["lon"]

                # Déterminer le type de bar
                amenity = element["tags"].get("amenity", "bar")
                bar_type = "Pub" if amenity == "pub" else "Bar"

                # Construire l'adresse approximative
                address_parts = []
                if "addr:housenumber" in element["tags"]:
                    address_parts.append(element["tags"]["addr:housenumber"])
                if "addr:street" in element["tags"]:
                    address_parts.append(element["tags"]["addr:street"])
                if "addr:postcode" in element["tags"]:
                    address_parts.append(element["tags"]["addr:postcode"])
                address_parts.append("Paris")

                address = (
                    ", ".join(address_parts)
                    if address_parts
                    else f"Près de {center_lat:.3f}, {center_lon:.3f}"
                )

                bars.append(
                    {
                        "name": name,
                        "lat": lat,
                        "lon": lon,
                        "address": address,
                        "type": bar_type,
                    }
                )

        # Si on trouve moins de 10 bars, ajouter quelques bars populaires connus
        if len(bars) < 10:
            fallback_bars = [
                {
                    "name": "Le Mary Celeste",
                    "lat": 48.8576,
                    "lon": 2.3639,
                    "address": "1 Rue Commines, 75003 Paris",
                    "type": "Bar à cocktails",
                },
                {
                    "name": "Hemingway Bar",
                    "lat": 48.8678,
                    "lon": 2.3281,
                    "address": "15 Pl. Vendôme, 75001 Paris",
                    "type": "Bar de luxe",
                },
                {
                    "name": "Prescription Cocktail Club",
                    "lat": 48.8566,
                    "lon": 2.3354,
                    "address": "23 Rue Mazarine, 75006 Paris",
                    "type": "Speakeasy",
                },
                {
                    "name": "Le Perchoir",
                    "lat": 48.8654,
                    "lon": 2.3734,
                    "address": "14 Rue Crespin du Gast, 75011 Paris",
                    "type": "Rooftop bar",
                },
                {
                    "name": "Little Red Door",
                    "lat": 48.8576,
                    "lon": 2.3639,
                    "address": "60 Rue Charlot, 75003 Paris",
                    "type": "Bar à cocktails",
                },
            ]

            # Ajouter les bars de fallback qui ne sont pas déjà dans la liste
            existing_names = {bar["name"].lower() for bar in bars}
            for fallback_bar in fallback_bars:
                if fallback_bar["name"].lower() not in existing_names:
                    bars.append(fallback_bar)
                    if len(bars) >= 15:  # Limiter à 15 bars max
                        break

        return bars[:20]  # Limiter à 20 bars maximum

    except Exception as e:
        st.error(f"Erreur lors de la recherche de bars: {str(e)}")
        # Retourner quelques bars populaires par défaut
        return [
            {
                "name": "Le Mary Celeste",
                "lat": 48.8576,
                "lon": 2.3639,
                "address": "1 Rue Commines, 75003 Paris",
                "type": "Bar à cocktails",
            },
            {
                "name": "Hemingway Bar",
                "lat": 48.8678,
                "lon": 2.3281,
                "address": "15 Pl. Vendôme, 75001 Paris",
                "type": "Bar de luxe",
            },
            {
                "name": "Prescription Cocktail Club",
                "lat": 48.8566,
                "lon": 2.3354,
                "address": "23 Rue Mazarine, 75006 Paris",
                "type": "Speakeasy",
            },
            {
                "name": "Le Perchoir",
                "lat": 48.8654,
                "lon": 2.3734,
                "address": "14 Rue Crespin du Gast, 75011 Paris",
                "type": "Rooftop bar",
            },
        ]


# Charger les amis
friends = load_friends()

if not friends:
    st.warning(
        "⚠️ Aucun ami enregistré ! Allez d'abord dans l'onglet 'Les Copaines' pour ajouter vos amis."
    )
    st.stop()

# Calculer le centre géographique des amis (barycentre)
center_lat, center_lon = calculate_center(friends)

# Afficher les informations du barycentre
st.subheader("📍 Centre du groupe d'amis")
col1, col2 = st.columns(2)

with col1:
    st.info(
        f"🎯 **Barycentre calculé :**\n\nLatitude: {center_lat:.4f}\nLongitude: {center_lon:.4f}"
    )

with col2:
    radius_km = st.slider(
        "🔍 Rayon de recherche (km)",
        min_value=0.5,
        max_value=5.0,
        value=2.0,
        step=0.5,
        help="Distance maximum pour rechercher les bars autour du centre du groupe",
    )

# Obtenir la liste des bars autour du barycentre
with st.spinner(
    f"🔍 Recherche des bars dans un rayon de {radius_km} km autour du centre du groupe..."
):
    bars = get_bars_around_center(center_lat, center_lon, radius_km=radius_km)

if not bars:
    st.warning(
        "⚠️ Aucun bar trouvé dans la zone. Essayez d'augmenter le rayon de recherche."
    )
    st.stop()

st.success(f"✅ {len(bars)} bars trouvés autour du centre du groupe")

# Calculer la distance moyenne pour chaque bar
for bar in bars:
    bar["avg_distance"] = calculate_average_distance(bar["lat"], bar["lon"], friends)

# Trier les bars par distance moyenne
bars_sorted = sorted(bars, key=lambda x: x["avg_distance"])

# Affichage des métriques
st.subheader("📊 Statistiques")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Amis enregistrés", len(friends))

with col2:
    st.metric("Bars trouvés", len(bars))

with col3:
    best_bar = bars_sorted[0]
    st.metric("Meilleur bar", best_bar["name"])

with col4:
    st.metric("Distance moyenne", f"{best_bar['avg_distance']:.1f} km")

# Créer la carte
st.subheader("🗺️ Carte interactive")

# Initialiser la carte centrée sur le groupe d'amis
m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="OpenStreetMap")

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
for friend in friends:
    if friend.get("latitude") and friend.get("longitude"):
        folium.Marker(
            [friend["latitude"], friend["longitude"]],
            popup=f"👤 {friend['name']}<br>{friend['address']}",
            icon=folium.Icon(color="blue", icon="user"),
        ).add_to(m)

# Ajouter les 5 meilleurs bars sur la carte
for i, bar in enumerate(bars_sorted[:5]):
    color = "red" if i == 0 else "orange" if i < 3 else "green"
    icon = "star" if i == 0 else "glass"

    folium.Marker(
        [bar["lat"], bar["lon"]],
        popup=f"🍻 {bar['name']}<br>{bar['type']}<br>Distance moyenne: {bar['avg_distance']:.1f} km",
        icon=folium.Icon(color=color, icon=icon),
    ).add_to(m)

# Afficher la carte
map_data = st_folium(m, width=700, height=500)

# Affichage de la liste des bars recommandés
st.subheader("🏆 Top 10 des bars recommandés")

# Créer un DataFrame pour l'affichage
df_bars = pd.DataFrame(bars_sorted[:10])
df_display = df_bars[["name", "type", "address", "avg_distance"]].copy()
df_display.columns = ["Nom du bar", "Type", "Adresse", "Distance moyenne (km)"]
df_display["Distance moyenne (km)"] = df_display["Distance moyenne (km)"].round(1)

# Ajouter des emojis pour le classement
rankings = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
df_display.insert(0, "Rang", rankings)

st.dataframe(df_display, use_container_width=True)

# Informations détaillées sur le meilleur bar
st.subheader("🎯 Recommandation principale")
best_bar = bars_sorted[0]

# Calculer la distance du bar au barycentre
distance_to_center = geodesic(
    (best_bar["lat"], best_bar["lon"]), (center_lat, center_lon)
).kilometers

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
    **🏆 {best_bar['name']}**
    
    📍 **Adresse :** {best_bar['address']}
    
    🍻 **Type :** {best_bar['type']}
    
    📏 **Distance moyenne :** {best_bar['avg_distance']:.1f} km de vos amis
    
    🎯 **Distance du centre :** {distance_to_center:.1f} km du barycentre
    """
    )

with col2:
    st.markdown("**📊 Distances individuelles :**")
    for friend in friends:
        if friend.get("latitude") and friend.get("longitude"):
            distance = geodesic(
                (best_bar["lat"], best_bar["lon"]),
                (friend["latitude"], friend["longitude"]),
            ).kilometers
            st.write(f"• {friend['name']}: {distance:.1f} km")

# Bouton pour rafraîchir les recommandations
if st.button("🔄 Recalculer les recommandations"):
    st.cache_data.clear()
    st.rerun()
