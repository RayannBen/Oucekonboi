#!/usr/bin/env python3
"""
Script de démonstration des améliorations de l'interface Streamlit.
Simule l'affichage des différences de temps et de l'ancien barycentre.
"""

import sys
import os

# Ajouter le dossier src au path Python
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.data_manager import load_friends
from src.geo_utils import calculate_center
from src.transit_utils import calculate_weighted_center_by_transit_time
from geopy.distance import geodesic


def demo_optimisation_interface():
    """Démonstration des nouvelles fonctionnalités d'interface."""
    print("🎨 DÉMONSTRATION DES AMÉLIORATIONS INTERFACE")
    print("=" * 60)

    # Charger les amis
    friends = load_friends()
    print(f"📋 Groupe de {len(friends)} amis chargé")

    # Calculer le barycentre géographique classique
    geo_lat, geo_lon = calculate_center(friends)
    print(f"📍 Barycentre géographique: {geo_lat:.6f}, {geo_lon:.6f}")

    # Mock des fonctions Streamlit pour simulation
    class MockST:
        @staticmethod
        def info(msg):
            pass

        @staticmethod
        def write(msg):
            pass

        @staticmethod
        def success(msg):
            pass

    # Simuler le calcul avec mock
    import src.transit_utils as transit_module

    original_st = transit_module.st
    transit_module.st = MockST()

    try:
        # Calculer le barycentre pondéré
        transit_lat, transit_lon, transit_times, calc_info = (
            calculate_weighted_center_by_transit_time(friends)
        )

        print("\n🎯 NOUVEAU DANS L'INTERFACE STREAMLIT:")
        print("=" * 60)

        print("\n1️⃣ MÉTRIQUES D'OPTIMISATION")
        print("-" * 30)
        print(f"⏱️ Temps initial moyen: {calc_info['avg_initial_time']:.0f} min")
        print(f"⏱️ Temps final moyen: {calc_info['avg_final_time']:.0f} min")
        improvement = calc_info["time_improvement"]
        emoji = "📈" if improvement > 0 else "📊"
        print(f"{emoji} Amélioration: {improvement:+.0f} min")
        print(f"📏 Déplacement: {calc_info['displacement_km']:.0f} mètres")

        print("\n2️⃣ COMPARAISON DÉTAILLÉE DES TEMPS")
        print("-" * 40)
        print("Ancien barycentre → Nouveau barycentre:")

        for name in friends:
            if (
                name["name"] in calc_info["initial_times"]
                and name["name"] in transit_times
            ):
                old_time = calc_info["initial_times"][name["name"]]
                new_time = transit_times[name["name"]]
                diff = new_time - old_time
                emoji = "✅" if diff <= 0 else "⚠️"
                print(
                    f"{emoji} {name['name']:12}: {old_time:4.0f} min → {new_time:4.0f} min ({diff:+4.0f})"
                )

        print("\n3️⃣ AMÉLIORATIONS DE LA CARTE")
        print("-" * 35)
        print("🔴 Marqueur rouge: Ancien barycentre géographique")
        print("🟢 Marqueur vert: Nouveau barycentre optimisé")
        print("🔄 Ligne pointillée: Déplacement d'optimisation")
        print("📏 Cercle violet: Zone de recherche des bars")
        print("🍻 Marqueurs bars: Temps de transport affiché si mode transport")

        print("\n4️⃣ DONNÉES POUR LA CARTE")
        print("-" * 25)
        print(
            f"Centre initial (rouge): {calc_info['initial_center'][0]:.6f}, {calc_info['initial_center'][1]:.6f}"
        )
        print(f"Centre optimisé (vert): {transit_lat:.6f}, {transit_lon:.6f}")

        # Calculer la distance réelle déplacée
        distance_moved = geodesic(
            calc_info["initial_center"], (transit_lat, transit_lon)
        ).meters
        print(f"Distance déplacée: {distance_moved:.0f} mètres")

        print("\n💡 L'utilisateur voit maintenant:")
        print("   - Les gains de temps individuels pour chaque ami")
        print("   - Le déplacement visuel du barycentre sur la carte")
        print("   - Les métriques d'amélioration en temps réel")
        print("   - La comparaison avant/après l'optimisation")

    finally:
        transit_module.st = original_st


if __name__ == "__main__":
    demo_optimisation_interface()
