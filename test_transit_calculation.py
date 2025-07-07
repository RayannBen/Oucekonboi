#!/usr/bin/env python3
"""
Script de test pour vérifier le calcul du barycentre pondéré par temps de transport.
"""

import sys
import os
import json

# Ajouter le dossier src au path Python
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.data_manager import load_friends
from src.geo_utils import calculate_center
from src.transit_utils import calculate_weighted_center_by_transit_time


def test_transit_calculation():
    """Test du calcul du barycentre pondéré."""
    print("🚇 Test du calcul du barycentre pondéré par temps de transport\n")

    # Charger les amis
    friends = load_friends()
    print(f"📋 Amis chargés: {len(friends)}")
    for friend in friends:
        print(f"  - {friend['name']}: {friend['address']}")
    print()

    # Calculer le barycentre géographique classique
    geo_lat, geo_lon = calculate_center(friends)
    print(f"📍 Barycentre géographique: {geo_lat:.6f}, {geo_lon:.6f}\n")

    print("=" * 60)
    print("🔄 CALCUL DU BARYCENTRE PONDÉRÉ PAR TEMPS DE TRANSPORT")
    print("=" * 60)

    # Simulation sans Streamlit (on va capturer les messages)
    # Pour cela, on va modifier temporairement les appels st.info/st.write

    # Importer le module sans Streamlit
    import importlib
    import src.transit_utils as transit_module

    # Mock des fonctions Streamlit pour affichage console
    class MockST:
        @staticmethod
        def info(msg):
            print(f"ℹ️  {msg}")

        @staticmethod
        def write(msg):
            print(f"   {msg}")

        @staticmethod
        def success(msg):
            print(f"✅ {msg}")

    # Remplacer temporairement st par notre mock
    original_st = transit_module.st
    transit_module.st = MockST()

    try:
        # Calculer le barycentre pondéré
        transit_lat, transit_lon, transit_times, calc_info = (
            calculate_weighted_center_by_transit_time(friends)
        )

        print("\n" + "=" * 60)
        print("📊 RÉSULTATS FINAUX")
        print("=" * 60)
        print(f"📍 Barycentre optimisé: {transit_lat:.6f}, {transit_lon:.6f}")
        print(
            f"📏 Déplacement depuis le centre géo: {calc_info.get('displacement_km', 0):.0f} mètres"
        )
        print(f"⏱️  Temps moyen initial: {calc_info.get('avg_initial_time', 0):.1f} min")
        print(f"⏱️  Temps moyen final: {calc_info.get('avg_final_time', 0):.1f} min")
        print(f"📈 Amélioration: {calc_info.get('time_improvement', 0):+.1f} min")

        print("\n🎯 Temps de trajet finaux vers le barycentre optimisé:")
        for name, time_min in transit_times.items():
            print(f"  🚇 {name}: {time_min:.1f} min")

    finally:
        # Remettre l'original
        transit_module.st = original_st


if __name__ == "__main__":
    test_transit_calculation()
