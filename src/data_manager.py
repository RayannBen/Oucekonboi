"""
Module pour la gestion des données des amis.
"""

import json
import os


DATA_FILE = "data/friends.json"


def load_friends():
    """
    Charge la liste des amis depuis le fichier JSON.

    Returns:
        list: Liste des amis avec leurs informations
    """
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_friends(friends):
    """
    Sauvegarde la liste des amis dans le fichier JSON.

    Args:
        friends (list): Liste des amis à sauvegarder
    """
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(friends, f, ensure_ascii=False, indent=2)
