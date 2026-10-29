"""
Point d'entrée en ligne de commande (orchestrateur, IMPUR).
Rôle : lit les arguments, charge la config, appelle les modules dans
l'ordre du pipeline, gère les erreurs (log + continue), écrit le JSON.
"""

import os
from pathlib import Path
import argparse
import sys
import time
from datetime import datetime

from debtect.config import est_exclu, peut_elaguer, charger
from debtect.complexity import calculer
from debtect.hotspot import score
from debtect.models import FileAnalysis
from debtect.parser import parser, ErreurParsing
from debtect.git_miner import churn, ErreurGit
from debtect.report import construire, vers_json


def _signaler_erreur_parcours(erreur: OSError) -> None:
    chemin = erreur.filename or "chemin inconnu"
    print(
        f"Avertissement : impossible de parcourir {chemin} : {erreur}",
        file=sys.stderr,
    )


def _decouvrir_fichiers(racine: Path, spec) -> list[Path]:
    fichiers = []
    elagage_autorise = peut_elaguer(spec)

    for dossier, sous_dossiers, noms_fichiers in os.walk(
        racine, topdown=True, onerror=_signaler_erreur_parcours
    ):
        chemin_dossier = Path(dossier)

        if elagage_autorise:
            sous_dossiers[:] = [
                nom
                for nom in sous_dossiers
                if not est_exclu(
                    spec,
                    (chemin_dossier / nom).relative_to(racine).as_posix() + "/",
                )
            ]

        for nom in noms_fichiers:
            if not nom.endswith(".php"):
                continue

            chemin = chemin_dossier / nom
            chemin_relatif = chemin.relative_to(racine).as_posix()

            if not est_exclu(spec, chemin_relatif):
                fichiers.append(chemin)

    return fichiers


def _analyser_fichier(
    chemin: Path,
    racine: Path,
    churn_dict: dict,
) -> FileAnalysis:
    cle = chemin.relative_to(racine).as_posix()
    ast = parser(str(chemin))
    fonctions = calculer(ast)
    complexite_totale = sum(fonction.complexite for fonction in fonctions)
    churn_fichier = churn_dict.get(cle, 0)
    score_hotspot = score(complexite_totale, churn_fichier)
    nb_lignes = len(ast.text.splitlines())
    return FileAnalysis(
        chemin=cle,
        nb_lignes=nb_lignes,
        fonctions=fonctions,
        complexite_totale=complexite_totale,
        churn=churn_fichier,
        score_hotspot=score_hotspot,
        dependances=[],
    )


def main(argv=None) -> int:
    analyseur = argparse.ArgumentParser(
        prog="debtect", description="Analyse la dette technique de projet PHP."
    )
    analyseur.add_argument("repo", help="chemin du dépôt Git à analyser.")
    analyseur.add_argument(
        "-o",
        "--sortie",
        default="analyse.json",
        help="Chemin du fichier JSON de sortie (défaut : analyse.json)",
    )

    args = analyseur.parse_args(argv)
    debut = time.perf_counter()
    racine = Path(args.repo).resolve()

    try:
        churn_dict = churn(str(racine))
    except ErreurGit as erreur:
        print(f"Erreur Git : {erreur}", file=sys.stderr)
        return 1

    try:
        spec = charger(str(racine))
        fichiers = _decouvrir_fichiers(racine, spec)
    except OSError as erreur:
        print(f"Erreur lors de la lecture du projet : {erreur}", file=sys.stderr)
        return 1

    analyses = []
    fichiers_echec = []

    for numero, chemin in enumerate(fichiers, start=1):
        try:
            resultat_fichier = _analyser_fichier(
                chemin,
                racine,
                churn_dict,
            )
            analyses.append(resultat_fichier)
        except (ErreurParsing, OSError) as erreur:
            chemin_relatif = chemin.relative_to(racine).as_posix()
            fichiers_echec.append(chemin_relatif)
            print(
                f"Avertissement : impossible d'analyser "
                f"{chemin_relatif} : {erreur}",
                file=sys.stderr,
            )

        if numero % 500 == 0:
            print(
                f"Progression : {numero}/{len(fichiers)} fichiers traités",
                file=sys.stderr,
            )

    duree = time.perf_counter() - debut
    date_analyse = datetime.now().isoformat(timespec="seconds")

    resultat = construire(
        chemin_projet=str(racine),
        date_analyse=date_analyse,
        duree=duree,
        fichiers=analyses,
        fichiers_echec=fichiers_echec,
    )

    chemin_sortie = Path(args.sortie)
    try:
        chemin_sortie.write_text(
            vers_json(resultat),
            encoding="utf-8",
        )
    except OSError as erreur:
        print(f"Erreur lors de l'écriture du rapport : {erreur}", file=sys.stderr)
        return 1

    print(f"Fichiers PHP découverts : {len(fichiers)}")
    print(f"Fichiers analysés avec succès : {len(analyses)}")
    print(f"Fichiers en échec : {len(fichiers_echec)}")
    print(f"Durée : {duree:.2f} secondes")
    print(f"Rapport JSON : {chemin_sortie.resolve()}")

    if fichiers_echec:
        print("\nFichiers en échec :")
        for chemin in resultat.fichiers_echec:
            print(f"  - {chemin}")

    print("\nTop 5 des fichiers à risque :")
    for fichier in resultat.fichiers[:5]:
        print(
            f"{fichier.chemin} | complexité={fichier.complexite_totale} | churn={fichier.churn} | score={fichier.score_hotspot}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
