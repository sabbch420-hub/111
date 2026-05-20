#!/usr/bin/env python3
"""
Script pour supprimer les mots-cles stopwords de keyword_index.
Usage: python cleanup_stopword_keywords.py
"""

from backend.base import keyword_index_collection
from backend.populate_keywords import STOPWORDS


def cleanup_stopwords() -> int:
    """Supprime les documents keyword_index dont le mot est un stopword."""
    print("Nettoyage des stopwords dans keyword_index...")

    if not STOPWORDS:
        print("Aucun stopword defini.")
        return 0

    result = keyword_index_collection.delete_many({"mot": {"$in": list(STOPWORDS)}})
    print(f"{result.deleted_count} documents supprimes.")
    return int(result.deleted_count or 0)


def cleanup_single_letter_alpha_tokens() -> int:
    """Supprime les tokens d'une seule lettre alphabetique (garde les chiffres)."""
    print("Nettoyage des tokens d'une lettre (alpha uniquement)...")
    result = keyword_index_collection.delete_many({"mot": {"$regex": r"^[a-z]$"}})
    print(f"{result.deleted_count} documents supprimes.")
    return int(result.deleted_count or 0)


if __name__ == "__main__":
    try:
        deleted_stopwords = cleanup_stopwords()
        deleted_single = cleanup_single_letter_alpha_tokens()
        total_deleted = deleted_stopwords + deleted_single
        print(f"\nNettoyage termine. {total_deleted} documents supprimes.")
    except Exception as exc:
        print(f"\nErreur lors du nettoyage: {exc}")
