
import time
from pathlib import Path
import os

from debtect.git_miner import churn
from debtect.parser import parser, ErreurParsing
from debtect.complexity import calculer
from debtect.hotspot import score
from debtect.config import charger, est_exclu, peut_elaguer

racine = Path(r"D:\Study\ProjFinAnnée\Test_PHP\akaunting")

churn_dict = churn(str(racine))


spec = charger(str(racine))

elagage_autorise = peut_elaguer(spec)

fichiers = []

for dossier, sous_dossiers, noms_fichiers in os.walk(racine, topdown=True):
    chemin_dossier = Path(dossier)

    # Sans négation, on peut ignorer les dossiers exclus
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



print("Fichiers PHP à analyser :", len(fichiers))
print("Chemins historiques dans churn :", len(churn_dict))


resultats = []
echecs = []

debut = time.perf_counter()

temps_parsing = 0.0
temps_calcul = 0.0

for chemin in fichiers:
    cle = chemin.relative_to(racine).as_posix()

    debut_parsing = time.perf_counter()
    try:
        ast = parser(str(chemin))
    except ErreurParsing:
        echecs.append(cle)
        continue
    finally:
        temps_parsing += time.perf_counter() - debut_parsing

    debut_calcul = time.perf_counter()
    fonctions = calculer(ast)
    temps_calcul += time.perf_counter() - debut_calcul

    complexites = [fonction.complexite for fonction in fonctions]

    somme = sum(complexites)
    maximum = max(complexites, default=0)
    commits = churn_dict.get(cle, 0)

    resultats.append((cle, somme, maximum, commits))

duree = time.perf_counter() - debut

print("Durée de la boucle :", round(duree, 2), "secondes")
print("Échecs de parsing :", len(echecs))
print("Résultats calculés :", len(resultats))
print(
    "Fichiers sans commits historiques :",
    sum(1 for _, _, _, commits in resultats if commits == 0),
)
print("Temps parsing :", round(temps_parsing, 2), "secondes")
print("Temps calcul :", round(temps_calcul, 2), "secondes")

# Classement selon la somme des complexités
classement_somme = sorted(
    resultats,
    key=lambda resultat: score(resultat[1], resultat[3]),
    reverse=True,
)[:10]


# Classement selon la complexité maximale
classement_maximum = sorted(
    resultats,
    key=lambda resultat: score(resultat[2], resultat[3]),
    reverse=True,
)[:10]


def afficher_classement(titre, classement, utiliser_maximum=False):
    print(f"\n{titre}")
    print("-" * len(titre))

    for rang, (chemin, somme, maximum, commits) in enumerate(
        classement, start=1
    ):
        complexite = maximum if utiliser_maximum else somme
        score_fichier = score(complexite, commits)

        print(
            f"{rang:2}. {chemin} | "
            f"somme={somme} | "
            f"maximum={maximum} | "
            f"commits={commits} | "
            f"score={score_fichier}"
        )


afficher_classement(
    "Top 10 — Score basé sur la somme",
    classement_somme,
)

afficher_classement(
    "Top 10 — Score basé sur le maximum",
    classement_maximum,
    utiliser_maximum=True,
)
