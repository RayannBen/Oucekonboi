"""
Module pour les composants de l'interface utilisateur.
"""

import streamlit as st
import pandas as pd
from geopy.distance import geodesic


def display_header():
    """Affiche l'en-tête de la page."""
    st.title("🍻 Oucekonboi - Trouveur de bars")
    st.markdown("### Découvrez les meilleurs bars proches de vos amis")


def display_no_friends_warning():
    """Affiche un avertissement si aucun ami n'est enregistré."""
    st.warning(
        "⚠️ Aucun ami enregistré ! Allez d'abord dans l'onglet 'Les Copaines' pour ajouter vos amis."
    )
    st.stop()


def display_center_info(center_lat, center_lon):
    """
    Affiche les informations sur le centre géographique.

    Args:
        center_lat (float): Latitude du centre
        center_lon (float): Longitude du centre

    Returns:
        float: Rayon de recherche sélectionné
    """
    st.subheader("📍 Centre du groupe d'amis")
    col1, col2 = st.columns(2)

    with col1:
        st.info(
            f"🎯 **Barycentre calculé :**\n\nLatitude: {center_lat:.4f}\nLongitude: {center_lon:.4f}"
        )

    with col2:
        radius_km = st.slider(
            "🔍 Rayon de recherche (km)",
            min_value=0.05,
            max_value=2.0,
            value=0.5,
            step=0.1,
            help="Distance maximum pour rechercher les bars autour du centre du groupe",
        )

    return radius_km


def display_search_results(bars_count):
    """
    Affiche les résultats de la recherche de bars.

    Args:
        bars_count (int): Nombre de bars trouvés
    """
    if bars_count == 0:
        st.warning(
            "⚠️ Aucun bar trouvé dans la zone. Essayez d'augmenter le rayon de recherche."
        )
        st.stop()

    st.success(f"✅ {bars_count} bars trouvés autour du centre du groupe")


def display_statistics(friends, bars, best_bar):
    """
    Affiche les statistiques de l'application.

    Args:
        friends (list): Liste des amis
        bars (list): Liste des bars
        best_bar (dict): Meilleur bar recommandé
    """
    st.subheader("📊 Statistiques")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Amis enregistrés", len(friends))

    with col2:
        st.metric("Bars trouvés", len(bars))

    with col3:
        st.metric("Meilleur bar", best_bar["name"])

    with col4:
        st.metric("Distance moyenne", f"{best_bar['avg_distance']:.1f} km")


def display_bars_ranking(bars_sorted):
    """
    Affiche le classement des bars recommandés.

    Args:
        bars_sorted (list): Liste des bars triés par distance
    """
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


def display_best_bar_details(best_bar, friends, center_lat, center_lon):
    """
    Affiche les détails du meilleur bar recommandé.

    Args:
        best_bar (dict): Meilleur bar
        friends (list): Liste des amis
        center_lat (float): Latitude du centre
        center_lon (float): Longitude du centre
    """
    st.subheader("🎯 Recommandation principale")

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


def display_refresh_button():
    """Affiche le bouton de rafraîchissement."""
    if st.button("🔄 Recalculer les recommandations"):
        st.cache_data.clear()
        st.rerun()
