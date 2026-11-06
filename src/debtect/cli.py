"""
Point d'entrée en ligne de commande (orchestrateur, IMPUR).
Rôle : lit les arguments, charge la config, appelle les modules dans
l'ordre du pipeline, gère les erreurs (log + continue), écrit le JSON.
"""


import os
import json
from pathlib import Path
import argparse
import sys
import time
from datetime import datetime
from dataclasses import replace

from debtect.config import est_exclu, peut_elaguer, charger
from debtect.complexity import calculer
from debtect.hotspot import score
from debtect.models import FileAnalysis, InfoDependances
from debtect.parser import parser, ErreurParsing
from debtect.git_miner import churn, ErreurGit
from debtect.report import construire, vers_json
from debtect.dependency_graph import extraire, resoudre, impact, ErreurImpact


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
) -> tuple[FileAnalysis, InfoDependances]:
    cle = chemin.relative_to(racine).as_posix()
    ast = parser(str(chemin))
    infos = extraire(ast)
    fonctions = calculer(ast)
    complexite_totale = sum(fonction.complexite for fonction in fonctions)
    churn_fichier = churn_dict.get(cle, 0)
    score_hotspot = score(complexite_totale, churn_fichier)
    nb_lignes = len(ast.text.splitlines())

    analyse = FileAnalysis(
        chemin=cle,
        nb_lignes=nb_lignes,
        fonctions=fonctions,
        complexite_totale=complexite_totale,
        churn=churn_fichier,
        score_hotspot=score_hotspot,
        dependances=[],
    )

    return analyse, infos


def _analyser(args) -> int:
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
    infos_dependances: dict[str, InfoDependances] = {}

    for numero, chemin in enumerate(fichiers, start=1):
        try:
            analyse, infos = _analyser_fichier(chemin, racine, churn_dict)
            analyses.append(analyse)
            infos_dependances[analyse.chemin] = infos
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

    graphe = resoudre(infos_dependances)

    analyses = [
        replace(analyse, dependances=graphe[analyse.chemin])
        for analyse in analyses
    ]

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
        chemin_sortie.write_text(vers_json(resultat), encoding="utf-8")
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
            f"{fichier.chemin} | complexité={fichier.complexite_totale} "
            f"| churn={fichier.churn} | score={fichier.score_hotspot}"
        )

    return 0


def _impact(args) -> int:
    if args.profondeur is not None and args.profondeur < 0:
        print("Erreur : la profondeur doit être positive ou nulle.", file=sys.stderr)
        return 1

    try:
        rapport = json.loads(Path(args.json).read_text(encoding="utf-8"))

        fichiers = {
            fichier["chemin"]: fichier
            for fichier in rapport["fichiers"]
        }
        dependances = {
            chemin: fichier["dependances"]
            for chemin, fichier in fichiers.items()
        }

        resultats = impact(
            dependances,
            args.fichier,
            profondeur=args.profondeur,
        )

    except ErreurImpact as erreur:
        print(f"Erreur d'impact : {erreur}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as erreur:
        print(f"Erreur lors de la lecture du rapport : {erreur}", file=sys.stderr)
        return 1

    if not resultats:
        print(f"Aucun fichier impacté par {args.fichier}.")
        return 0

    niveaux = sorted(set(resultats.values()))
    print(f"Fichiers impactés par {args.fichier} : {len(resultats)}")

    for niveau in niveaux:
        fichiers_niveau = [
            chemin for chemin, distance in resultats.items()
            if distance == niveau
        ]
        fichiers_niveau.sort(
            key=lambda c: (-fichiers[c]["score_hotspot"], c)
        )

        print(f"\nNiveau {niveau} :")

        affiches = fichiers_niveau if args.tout else fichiers_niveau[:10]
        
        for chemin in affiches:
            score_fichier = fichiers[chemin]["score_hotspot"]
            print(f"  {chemin} | score={score_fichier}")
        
        if not args.tout and len(fichiers_niveau) > 10:
            print(f"  ... et {len(fichiers_niveau) - 10} autres fichiers")

    return 0


def main(argv=None) -> int:
    analyseur = argparse.ArgumentParser(
        prog="debtect",
        description="Analyse la dette technique de projet PHP.",
    )
    commandes = analyseur.add_subparsers(dest="commande", required=True)

    commande_analyser = commandes.add_parser(
        "analyser",
        help="Analyse un dépôt PHP.",
    )
    commande_analyser.add_argument("repo", help="Chemin du dépôt Git à analyser.")
    commande_analyser.add_argument(
        "-o",
        "--sortie",
        default="analyse.json",
        help="Chemin du fichier JSON de sortie (défaut : analyse.json)",
    )

    commande_impact = commandes.add_parser(
        "impact",
        help="Recherche les fichiers impactés par une cible.",
    )
    commande_impact.add_argument("json", help="Rapport JSON d'analyse.")
    commande_impact.add_argument("fichier", help="Chemin du fichier cible.")
    commande_impact.add_argument(
        "--profondeur",
        type=int,
        default=None,
        help="Profondeur maximale du parcours.",
    )

    commande_impact.add_argument(
        "--tout",
        action="store_true",
        help="Affiche tous les fichiers impactés.",
    )

    args = analyseur.parse_args(argv)

    if args.commande == "analyser":
        return _analyser(args)

    if args.commande == "impact":
        return _impact(args)

    return 1


if __name__ == "__main__":
    sys.exit(main())
