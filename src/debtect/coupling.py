"""Couplage temporel (F6) — PUR. Co-modification entre fichiers à partir des commits."""


from collections import Counter
from itertools import combinations
from dataclasses import replace

from debtect.models import Couplage

def calculer_couplages(
    commits: list[list[str]],
    fichiers_connus: set[str],
    min_communs: int = 5,
    min_degre: float = 0.3,
    taille_max: int = 30,
    limite: int = 200,
) -> list[Couplage]:
    commits_par_fichier = Counter()
    commits_par_paire = Counter()

    for commit in commits:
        fichiers = sorted(set(commit) & fichiers_connus)

        if not fichiers or len(fichiers) > taille_max:
            continue

        commits_par_fichier.update(fichiers)

        if len(fichiers) >= 2:
            commits_par_paire.update(combinations(fichiers, 2))

    resultats = []

    for (fichier_a, fichier_b), nb_communs in commits_par_paire.items():
        if nb_communs < min_communs:
            continue

        moyenne = (
            commits_par_fichier[fichier_a] + commits_par_fichier[fichier_b]
        ) / 2

        if moyenne == 0:
            continue

        degre = nb_communs / moyenne

        if degre >= min_degre:
            resultats.append(
                Couplage(
                    fichier_a=fichier_a,
                    fichier_b=fichier_b,
                    commits_communs=nb_communs,
                    degre=degre,
                    lien_statique=False,
                )
            )

    resultats.sort(
        key=lambda c: (
            -c.degre,
            -c.commits_communs,
            c.fichier_a,
            c.fichier_b,
        )
    )

    return resultats[:limite]

def croiser(couplages, dependances):
    resultat = []

    for couplage in couplages:
        lien_statique = (
            couplage.fichier_b in dependances.get(couplage.fichier_a, [])
            or couplage.fichier_a in dependances.get(couplage.fichier_b, [])
        )

        resultat.append(
            replace(couplage, lien_statique=lien_statique)
        )

    return resultat