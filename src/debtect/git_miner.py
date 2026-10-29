"""Extraction du churn Git (F3) — IMPUR. Un seul appel global à l'historique."""

import subprocess
from collections import Counter
from pathlib import Path


class ErreurGit(Exception):
    pass


def _compter(texte: str) -> dict:
    lignes = texte.splitlines()
    fichiers = [ligne.strip() for ligne in lignes if ligne.strip()]
    return dict(Counter(fichiers))


def churn(repo: str) -> dict:
    chemin_repo = Path(repo).resolve()
    if not chemin_repo.is_dir():
        raise ErreurGit(
            f"Le chemin dépôt n'existe pas ou n'est pas un dossier : {repo}"
        )

    try:
        verification = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=chemin_repo,
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise ErreurGit(f"Échec de Git dans le dépôt : {repo} : {e.stderr}") from e
    except FileNotFoundError as e:
        raise ErreurGit("Git introuvable. Vérifie son installation et le PATH") from e

    racine_git = Path(verification.stdout.strip()).resolve()
    if racine_git != chemin_repo:
        raise ErreurGit(
            f"Le dossier fourni n'est pas la racine d'un dépôt Git : {repo}"
        )

    try:
        resultat = subprocess.run(
            [
                "git",
                "-c",
                "core.quotepath=false",
                "log",
                "--name-only",
                "--pretty=format:",
                "--",
                "*.php",
            ],
            cwd=chemin_repo,
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise ErreurGit(f"Échec de Git dans le dépôt : {repo} : {e.stderr}") from e
    except FileNotFoundError as e:
        raise ErreurGit("Git introuvable. Vérifie son installation et le PATH") from e

    return _compter(resultat.stdout)
