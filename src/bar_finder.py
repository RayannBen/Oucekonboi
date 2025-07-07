"""
Module pour la recherche de bars via l'API Overpass.
"""

import requests
import streamlit as st


@st.cache_data
def get_bars_around_center(center_lat, center_lon, radius_km: float = 0.6):
    """
    Recherche des bars autour du centre géographique du groupe d'amis
    en utilisant l'API Overpass d'OpenStreetMap.

    Args:
        center_lat (float): Latitude du centre
        center_lon (float): Longitude du centre
        radius_km (float): Rayon de recherche en kilomètres

    Returns:
        list: Liste des bars trouvés avec leurs informations
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

                # Ajouter la ville selon la position
                if (
                    center_lat >= 48.8
                    and center_lat <= 48.9
                    and center_lon >= 2.2
                    and center_lon <= 2.5
                ):
                    address_parts.append("Paris")
                else:
                    address_parts.append("France")

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
            bars.extend(get_fallback_bars(center_lat, center_lon))

        return bars[:10]  # Limiter à 10 bars maximum

    except Exception as e:
        st.error(f"Erreur lors de la recherche de bars: {str(e)}")
        return get_fallback_bars(center_lat, center_lon)


def get_fallback_bars(center_lat, center_lon):
    """
    Retourne une liste de bars populaires de fallback.

    Args:
        center_lat (float): Latitude du centre
        center_lon (float): Longitude du centre

    Returns:
        list: Liste des bars de fallback
    """
    # Bars populaires parisiens par défaut
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

    return fallback_bars
