import os
from pathlib import Path

from debtect.config import charger, est_exclu, peut_elaguer

racine = Path(r"D:\Study\ProjFinAnnée\Test_PHP\akaunting")

spec = charger(str(racine))

if not peut_elaguer(spec):
    raise RuntimeError("L'élagage est désactivé. Vérifie le fichier .debtectignore.")


def decouvrir_fichiers(elagage: bool) -> set[str]:
    fichiers = set()

    for dossier, sous_dossiers, noms_fichiers in os.walk(racine, topdown=True):
        chemin_dossier = Path(dossier)

        if elagage:
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
            relatif = chemin.relative_to(racine).as_posix()

            if not est_exclu(spec, relatif):
                fichiers.add(relatif)

    return fichiers


sans_elagage = decouvrir_fichiers(elagage=False)
avec_elagage = decouvrir_fichiers(elagage=True)

print("Sans élagage :", len(sans_elagage))
print("Avec élagage :", len(avec_elagage))
print("Fichiers manquants avec élagage :", len(sans_elagage - avec_elagage))
print("Fichiers supplémentaires avec élagage :", len(avec_elagage - sans_elagage))

if sans_elagage == avec_elagage:
    print("RÉSULTAT : ÉQUIVALENCE VALIDÉE")
else:
    print("RÉSULTAT : DIFFÉRENCE DÉTECTÉE")

    print("\nPrésents sans élagage, absents avec élagage :")
    for chemin in sorted(sans_elagage - avec_elagage):
        print("  ", chemin)

    print("\nPrésents avec élagage, absents sans élagage :")
    for chemin in sorted(avec_elagage - sans_elagage):
        print("  ", chemin)
