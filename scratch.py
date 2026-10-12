
import time
from pathlib import Path

from debtect.git_miner import churn
from debtect.parser import parser, ErreurParsing
from debtect.complexity import calculer
from debtect.hotspot import score


racine = Path(r"D:\Study\ProjFinAnnée\Test_PHP\akaunting")

churn_dict = churn(str(racine))

exclusions = {"vendor", "node_modules", ".git", "storage"}

fichiers = [
    chemin
    for chemin in racine.rglob("*.php")
    if not any(partie in exclusions for partie in chemin.relative_to(racine).parts)
]

print("Fichiers PHP à analyser :", len(fichiers))
print("Chemins historiques dans churn :", len(churn_dict))


resultats = []
echecs = []

debut = time.perf_counter()

for chemin in fichiers:
    cle = chemin.relative_to(racine).as_posix()

    try:
        ast = parser(str(chemin))
    except ErreurParsing:
        echecs.append(cle)
        continue

    fonctions = calculer(ast)
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
