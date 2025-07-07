import streamlit as st
import pandas as pd
import json
import os
from geopy.geocoders import Nominatim

st.title("👥 Les Copaines")
st.markdown("### Inscrivez vos amis et leurs adresses")

# Fichier pour stocker les données des amis
DATA_FILE = "data/friends.json"


# Fonction pour charger les données
def load_friends():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# Fonction pour sauvegarder les données
def save_friends(friends):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(friends, f, ensure_ascii=False, indent=2)


# Fonction pour géocoder une adresse
@st.cache_data
def geocode_address(address):
    try:
        geolocator = Nominatim(user_agent="oucekonboi_app")
        location = geolocator.geocode(f"{address}, Paris, France")
        if location:
            return location.latitude, location.longitude
        return None, None
    except:
        return None, None


# Charger les amis existants
friends = load_friends()

# Formulaire d'ajout d'un ami
st.subheader("➕ Ajouter un ami")

with st.form("add_friend"):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Nom de l'ami", placeholder="Ex: Alice")
        email = st.text_input("Email (optionnel)", placeholder="alice@example.com")

    with col2:
        address = st.text_area(
            "Adresse à Paris", placeholder="Ex: 15 rue de Rivoli, 75001 Paris"
        )

    submitted = st.form_submit_button("Ajouter l'ami")

    if submitted:
        if name and address:
            # Géocoder l'adresse
            with st.spinner("Vérification de l'adresse..."):
                lat, lon = geocode_address(address)

            if lat and lon:
                # Vérifier si l'ami existe déjà
                existing_friend = next(
                    (f for f in friends if f["name"].lower() == name.lower()), None
                )

                if existing_friend:
                    st.warning(
                        f"Un ami nommé {name} existe déjà. Mise à jour de ses informations."
                    )
                    existing_friend["email"] = email
                    existing_friend["address"] = address
                    existing_friend["latitude"] = lat
                    existing_friend["longitude"] = lon
                else:
                    # Ajouter le nouvel ami
                    new_friend = {
                        "name": name,
                        "email": email,
                        "address": address,
                        "latitude": lat,
                        "longitude": lon,
                    }
                    friends.append(new_friend)

                # Sauvegarder
                save_friends(friends)
                st.success(f"✅ {name} a été ajouté avec succès!")
                st.rerun()
            else:
                st.error(
                    "❌ Impossible de localiser cette adresse. Vérifiez qu'elle est bien à Paris."
                )
        else:
            st.error("❌ Veuillez remplir au moins le nom et l'adresse.")

# Affichage des amis enregistrés
st.subheader("📋 Amis enregistrés")

if friends:
    # Créer un DataFrame pour l'affichage
    df_display = pd.DataFrame(friends)
    df_display = df_display[["name", "email", "address"]].fillna("")
    df_display.columns = ["Nom", "Email", "Adresse"]

    st.dataframe(df_display, use_container_width=True)

    # Section de suppression
    st.subheader("🗑️ Supprimer un ami")
    friend_to_delete = st.selectbox(
        "Choisissez l'ami à supprimer:",
        options=[""] + [f["name"] for f in friends],
        key="delete_friend",
    )

    if friend_to_delete:
        if st.button(f"Supprimer {friend_to_delete}", type="secondary"):
            friends = [f for f in friends if f["name"] != friend_to_delete]
            save_friends(friends)
            st.success(f"✅ {friend_to_delete} a été supprimé.")
            st.rerun()

    # Statistiques
    st.subheader("📊 Statistiques")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Nombre d'amis", len(friends))

    with col2:
        emails_count = len([f for f in friends if f.get("email")])
        st.metric("Emails renseignés", emails_count)

    with col3:
        valid_addresses = len([f for f in friends if f.get("latitude")])
        st.metric("Adresses valides", valid_addresses)

else:
    st.info(
        "👥 Aucun ami enregistré pour le moment. Ajoutez votre premier ami ci-dessus !"
    )

    # Exemple pour aider l'utilisateur
    st.markdown(
        """
    **💡 Exemples d'adresses valides à Paris :**
    - 1 Place de la Concorde, 75001 Paris
    - 15 Avenue des Champs-Élysées, 75008 Paris
    - 5 Avenue Anatole France, 75007 Paris (Tour Eiffel)
    """
    )
