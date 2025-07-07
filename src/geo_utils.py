"""
Module pour les calculs géographiques et de distances.
"""

import numpy as np
from geopy.distance import geodesic


def calculate_center(friends):
    """
    Calcule le centre géographique (barycentre) d'un groupe d'amis.

    Args:
        friends (list): Liste des amis avec leurs coordonnées

    Returns:
        tuple: (latitude, longitude) du centre géographique
    """
    if not friends:
        return 48.8566, 2.3522  # Centre de Paris par défaut

    lats = [f["latitude"] for f in friends if f.get("latitude")]
    lons = [f["longitude"] for f in friends if f.get("longitude")]

    if not lats:
        return 48.8566, 2.3522

    return float(np.mean(lats)), float(np.mean(lons))


def calculate_average_distance(bar_lat, bar_lon, friends):
    """
    Calcule la distance moyenne d'un bar par rapport à un groupe d'amis.

    Args:
        bar_lat (float): Latitude du bar
        bar_lon (float): Longitude du bar
        friends (list): Liste des amis avec leurs coordonnées

    Returns:
        float: Distance moyenne en kilomètres
    """
    distances = []
    for friend in friends:
        if friend.get("latitude") and friend.get("longitude"):
            distance = geodesic(
                (bar_lat, bar_lon), (friend["latitude"], friend["longitude"])
            ).kilometers
            distances.append(distance)

    return np.mean(distances) if distances else float("inf")


def calculate_distance_to_center(bar_lat, bar_lon, center_lat, center_lon):
    """
    Calcule la distance d'un bar au centre géographique du groupe.

    Args:
        bar_lat (float): Latitude du bar
        bar_lon (float): Longitude du bar
        center_lat (float): Latitude du centre
        center_lon (float): Longitude du centre

    Returns:
        float: Distance en kilomètres
    """
    return geodesic((bar_lat, bar_lon), (center_lat, center_lon)).kilometers
