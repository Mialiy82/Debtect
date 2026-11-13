"""Extraction du churn Git (F3) — IMPUR. Un seul appel global à l'historique."""

import subprocess
from collections import Counter
from pathlib import Path


def creer_depot_git(chemin):
    subprocess.run(
        ["git", "init"],
        cwd=chemin,
        capture_output=True,
        check=True,
    )

    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=chemin,
        check=True,
    )

    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=chemin,
        check=True,
    )


def creer_commit(chemin):
    subprocess.run(
        ["git", "add", "."],
        cwd=chemin,
        capture_output=True,
        check=True,
    )

    subprocess.run(
        ["git", "commit", "-m", "Commit de test"],
        cwd=chemin,
        capture_output=True,
        check=True,
    )
    
class ErreurGit(Exception):
    pass

def _executer_git(arguments: list[str], repo: Path) -> str:
    try:
        resultat = subprocess.run(
            arguments,
            cwd=repo,
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise ErreurGit(
            f"Échec de Git dans le dépôt : {repo} : {e.stderr}"
        ) from e
    except FileNotFoundError as e:
        raise ErreurGit(
            "Git introuvable. Vérifie son installation et le PATH"
        ) from e

    return resultat.stdout

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

    verification = _executer_git(
        ["git", "rev-parse", "--show-toplevel"],
        chemin_repo,
    )

    racine_git = Path(verification.strip()).resolve()

    if racine_git != chemin_repo:
        raise ErreurGit(
            f"Le dossier fourni n'est pas la racine d'un dépôt Git : {repo}"
        )

    texte = _executer_git(
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
        chemin_repo,
    )

    return _compter(texte)

def commits(repo: str) -> list[list[str]]:
    chemin_repo = Path(repo).resolve()

    if not chemin_repo.is_dir():
        raise ErreurGit(
            f"Le chemin dépôt n'existe pas ou n'est pas un dossier : {repo}"
        )

    verification = _executer_git(
        ["git", "rev-parse", "--show-toplevel"],
        chemin_repo,
    )

    racine_git = Path(verification.strip()).resolve()

    if racine_git != chemin_repo:
        raise ErreurGit(
            f"Le dossier fourni n'est pas la racine d'un dépôt Git : {repo}"
        )

    texte = _executer_git(
        [
            "git",
            "-c",
            "core.quotepath=false",
            "log",
            "--name-only",
            "--pretty=format:%x1e",
            "--",
            "*.php",
        ],
        chemin_repo,
    )

    resultat = []

    for bloc in texte.split("\x1e"):
        fichiers = [
            ligne.strip()
            for ligne in bloc.splitlines()
            if ligne.strip()
        ]

        if fichiers:
            resultat.append(fichiers)

    return resultat