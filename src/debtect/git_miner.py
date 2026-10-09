"""Extraction du churn Git (F3) — IMPUR. Un seul appel global à l'historique."""

import subprocess
from collections import Counter

class ErreurGit(Exception):
  pass

def _compter(texte: str) -> dict :
  lignes = texte.splitlines()
  fichiers = [
    ligne.strip()
    for ligne in lignes
    if ligne.strip()
  ]
  return dict(Counter(fichiers))