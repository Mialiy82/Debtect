
import json

from debtect.models import FileAnalysis
from debtect.report import construire, vers_json


def creer_fichier(chemin: str, score: float) -> FileAnalysis:
    return FileAnalysis(
        chemin=chemin,
        lignes_code=0,
        fonctions=[],
        complexite_totale=0,
        churn=0,
        score_hotspot=score,
        erreur_parsing=None,
        dependances=[],
    )


fichiers = [
    creer_fichier("z.php", 10.0),
    creer_fichier("b.php", 50.0),
    creer_fichier("a.php", 50.0),
    creer_fichier("été.php", 25.0),
]

ordre_initial = [f.chemin for f in fichiers]

echecs = ["z.php", "a.php", "m.php"]

resultat = construire(
    chemin_projet="test",
    date_analyse="2026-10-14",
    duree=1.0,
    fichiers=fichiers,
    fichiers_echec=echecs,
)

# Étape 1 : tri des fichiers et pureté
print("Ordre des fichiers :", [f.chemin for f in resultat.fichiers])
print("Liste fichiers initiale préservée :",
      [f.chemin for f in fichiers] == ordre_initial)

# Vérification du tri et de la pureté des fichiers en échec
print("Fichiers en échec triés :", resultat.fichiers_echec)
print("Liste des échecs initiale :", echecs)
print("Même objet pour les listes d'échecs :",
      resultat.fichiers_echec is echecs)

# Étape 2 : conversion en JSON
texte_json = vers_json(resultat)
print("\nJSON produit :")
print(texte_json)

# Étape 3 : aller-retour JSON
donnees = json.loads(texte_json)
fichier_test = next(
    f for f in donnees["fichiers"]
    if f["chemin"] == "été.php"
)

print("\nChemin avec accent :", fichier_test["chemin"])
print("Erreur de parsing :", fichier_test["erreur_parsing"])
print("Clés de FileAnalysis :", list(fichier_test.keys()))
