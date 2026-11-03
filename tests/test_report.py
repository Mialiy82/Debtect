from debtect.models import FileAnalysis
from debtect.report import construire, vers_json


def creer_fichier(chemin: str, score: float) -> FileAnalysis:
    return FileAnalysis(
        chemin=chemin,
        nb_lignes=0,
        fonctions=[],
        complexite_totale=0,
        churn=0,
        score_hotspot=score,
        dependances=[],
    )


def test_tri_score_et_chemin():
    fichiers = [
        creer_fichier("z.php", 10.0),
        creer_fichier("b.php", 50.0),
        creer_fichier("a.php", 50.0),
        creer_fichier("c.php", 25.0),
    ]

    resultat = construire(
        chemin_projet="test",
        date_analyse="2026-10-14",
        duree=1.0,
        fichiers=fichiers,
        fichiers_echec=[],
    )

    chemins = [f.chemin for f in resultat.fichiers]

    assert chemins == ["a.php", "b.php", "c.php", "z.php"]


def test_construire_ne_modifie_pas_fichiers():
    fichiers = [
        creer_fichier("z.php", 10.0),
        creer_fichier("a.php", 50.0),
    ]

    fichiers_avant = fichiers.copy()

    construire(
        chemin_projet="test",
        date_analyse="2026-10-14",
        duree=1.0,
        fichiers=fichiers,
        fichiers_echec=[],
    )

    assert fichiers == fichiers_avant


def test_construire_copie_fichiers_echec():
    fichiers_echec = ["z.php", "a.php", "m.php"]

    resultat = construire(
        chemin_projet="test",
        date_analyse="2026-10-14",
        duree=1.0,
        fichiers=[],
        fichiers_echec=fichiers_echec,
    )

    assert resultat.fichiers_echec == ["a.php", "m.php", "z.php"]
    assert resultat.fichiers_echec is not fichiers_echec
    assert fichiers_echec == ["z.php", "a.php", "m.php"]


def test_json_cles_et_caractere_unicode():
    fichiers = [creer_fichier("été.php", 25.0)]

    resultat = construire(
        chemin_projet="test",
        date_analyse="2026-10-14",
        duree=1.0,
        fichiers=fichiers,
        fichiers_echec=[],
    )

    json_resultat = vers_json(resultat)

    assert '"chemin": "été.php"' in json_resultat

    import json

    donnees = json.loads(json_resultat)

    assert set(donnees["fichiers"][0].keys()) == {
        "chemin",
        "nb_lignes",
        "fonctions",
        "complexite_totale",
        "churn",
        "score_hotspot",
        "dependances",
    }
