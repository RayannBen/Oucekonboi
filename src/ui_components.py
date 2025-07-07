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
            value=0.6,
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


def display_statistics(
    friends, bars, best_bar, metric_type="Distance moyenne", metric_unit="km"
):
    """
    Affiche les statistiques de l'application.

    Args:
        friends (list): Liste des amis
        bars (list): Liste des bars
        best_bar (dict): Meilleur bar recommandé
        metric_type (str): Type de métrique (Distance/Temps)
        metric_unit (str): Unité de la métrique (km/min)
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
        value = best_bar.get("avg_time", best_bar.get("avg_distance", 0))
        st.metric(metric_type, f"{value:.1f} {metric_unit}")


def display_bars_ranking(bars_sorted, metric_type="Distance moyenne", metric_unit="km"):
    """
    Affiche le classement des bars recommandés.

    Args:
        bars_sorted (list): Liste des bars triés par distance/temps
        metric_type (str): Type de métrique
        metric_unit (str): Unité de métrique
    """
    st.subheader("🏆 Top 10 des bars recommandés")

    # Créer un DataFrame pour l'affichage
    df_bars = pd.DataFrame(bars_sorted[:10])

    # Choisir la colonne métrique appropriée
    metric_col = "avg_time" if "avg_time" in df_bars.columns else "avg_distance"

    df_display = df_bars[["name", "type", "address", metric_col]].copy()
    df_display.columns = [
        "Nom du bar",
        "Type",
        "Adresse",
        f"{metric_type} ({metric_unit})",
    ]
    df_display[f"{metric_type} ({metric_unit})"] = df_display[
        f"{metric_type} ({metric_unit})"
    ].round(1)

    # Ajouter des emojis pour le classement
    bar_number = len(df_display)
    medals_number_to_add = (bar_number - 3) if bar_number != 10 else 7
    rankings = ["🥇", "🥈", "🥉"] + ["🏅"] * medals_number_to_add
    df_display.insert(0, "Rang", rankings)

    st.dataframe(df_display, use_container_width=True)


def display_best_bar_details(
    best_bar,
    friends,
    center_lat,
    center_lon,
    use_transit=False,
    metric_type="Distance moyenne",
    metric_unit="km",
):
    """
    Affiche les détails du meilleur bar recommandé.

    Args:
        best_bar (dict): Meilleur bar
        friends (list): Liste des amis
        center_lat (float): Latitude du centre
        center_lon (float): Longitude du centre
        use_transit (bool): Si True, utilise les temps de transport
        metric_type (str): Type de métrique
        metric_unit (str): Unité de métrique
    """
    st.subheader("🎯 Recommandation principale")

    # Calculer la distance/temps du bar au barycentre
    if use_transit:
        from src.transit_utils import get_transit_time

        time_to_center = get_transit_time(
            best_bar["lat"], best_bar["lon"], center_lat, center_lon
        )
        center_metric = f"{time_to_center:.0f} min"
        center_label = "🚇 Temps vers le centre"
    else:
        distance_to_center = geodesic(
            (best_bar["lat"], best_bar["lon"]), (center_lat, center_lon)
        ).kilometers
        center_metric = f"{distance_to_center:.1f} km"
        center_label = "🎯 Distance du centre"

    col1, col2 = st.columns(2)

    with col1:
        main_value = best_bar.get("avg_time", best_bar.get("avg_distance", 0))
        st.markdown(
            f"""
        **🏆 {best_bar['name']}**
        
        📍 **Adresse :** {best_bar['address']}
        
        🍻 **Type :** {best_bar['type']}
        
        📏 **{metric_type} :** {main_value:.1f} {metric_unit} de vos amis
        
        {center_label} :** {center_metric} du barycentre
        """
        )

    with col2:
        st.markdown(f"**📊 {metric_type} individuelles :**")

        if use_transit:
            from src.transit_utils import get_transit_time

            for friend in friends:
                if friend.get("latitude") and friend.get("longitude"):
                    time_minutes = get_transit_time(
                        friend["latitude"],
                        friend["longitude"],
                        best_bar["lat"],
                        best_bar["lon"],
                    )
                    st.write(f"🚇 {friend['name']}: {time_minutes:.0f} min")
        else:
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
