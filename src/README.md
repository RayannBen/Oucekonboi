# Structure modulaire de l'application Oucekonboi

## Organisation du code

### 📁 Dossier `src/`
Le code a été réorganisé en modules spécialisés pour une meilleure maintenabilité :

#### 📋 `data_manager.py`
- **Fonction** : Gestion des données des amis
- **Fonctions principales** :
  - `load_friends()` : Charge la liste des amis depuis le JSON
  - `save_friends(friends)` : Sauvegarde la liste des amis

#### 🌍 `geo_utils.py`
- **Fonction** : Calculs géographiques et de distances
- **Fonctions principales** :
  - `calculate_center(friends)` : Calcule le barycentre du groupe
  - `calculate_average_distance(bar_lat, bar_lon, friends)` : Distance moyenne d'un bar
  - `calculate_distance_to_center(bar_lat, bar_lon, center_lat, center_lon)` : Distance au centre

#### 🔍 `bar_finder.py`
- **Fonction** : Recherche de bars via l'API Overpass
- **Fonctions principales** :
  - `get_bars_around_center(center_lat, center_lon, radius_km)` : Recherche les bars
  - `get_fallback_bars(center_lat, center_lon)` : Bars de secours

#### 🗺️ `map_utils.py`
- **Fonction** : Création et gestion des cartes interactives
- **Fonctions principales** :
  - `create_interactive_map()` : Crée la carte principale
  - `add_friends_to_map()` : Ajoute les marqueurs d'amis
  - `add_bars_to_map()` : Ajoute les marqueurs de bars
  - `display_map()` : Affiche la carte dans Streamlit

#### 🎨 `ui_components.py`
- **Fonction** : Composants de l'interface utilisateur
- **Fonctions principales** :
  - `display_header()` : En-tête de la page
  - `display_center_info()` : Informations du barycentre
  - `display_statistics()` : Métriques de l'application
  - `display_bars_ranking()` : Classement des bars
  - `display_best_bar_details()` : Détails du meilleur bar

### 📄 `Oucekonboi.py` (fichier principal)
Le fichier principal est maintenant beaucoup plus simple et lisible :
- Import des modules
- Orchestration des différentes fonctions
- Logique principale de l'application

## Avantages de cette architecture

### ✅ **Maintenabilité**
- Code organisé par responsabilité
- Fonctions réutilisables
- Facile à déboguer et modifier

### ✅ **Lisibilité**
- Fichier principal plus court et clair
- Chaque module a une fonction spécifique
- Documentation claire de chaque fonction

### ✅ **Extensibilité**
- Facile d'ajouter de nouvelles fonctionnalités
- Modules indépendants
- Tests unitaires possibles

### ✅ **Réutilisabilité**
- Fonctions peuvent être utilisées dans d'autres parties de l'app
- Code modulaire et paramétrable

## Utilisation

L'application fonctionne exactement comme avant, mais avec un code mieux organisé. Aucun changement pour l'utilisateur final !
