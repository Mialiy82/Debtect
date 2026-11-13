
from debtect.coupling import calculer_couplages
from debtect.models import Couplage
from debtect.coupling import croiser
import pytest

def test_calcul_couplage_nominal():
    commits = [
        ["a.php", "b.php"],
        ["a.php", "b.php"],
        ["a.php", "c.php"],
    ]

    resultat = calculer_couplages(
        commits,
        {"a.php", "b.php", "c.php"},
        min_communs=2,
        min_degre=0,
    )

    assert len(resultat) == 1
    assert resultat[0].fichier_a == "a.php"
    assert resultat[0].fichier_b == "b.php"
    assert resultat[0].commits_communs == 2
    assert resultat[0].degre == 0.8


def test_couplage_ignore_commit_trop_volumineux():
    fichiers = {f"{i}.php" for i in range(31)}

    resultat = calculer_couplages(
        [list(fichiers)],
        fichiers,
        min_communs=1,
        min_degre=0,
    )

    assert resultat == []


def test_couplage_ignore_fichiers_inconnus():
    commits = [
        ["a.php", "b.php", "inconnu.php"],
        ["a.php", "b.php", "inconnu.php"],
    ]

    resultat = calculer_couplages(
        commits,
        {"a.php", "b.php"},
        min_communs=2,
        min_degre=0,
    )

    assert len(resultat) == 1
    assert resultat[0].fichier_a== "a.php"
    assert resultat[0].fichier_b == "b.php"


def test_couplage_tri_deterministe():
    commits = [
        ["a.php", "b.php", "c.php"],
        ["a.php", "b.php", "c.php"],
    ]

    resultat = calculer_couplages(
        commits,
        {"a.php", "b.php", "c.php"},
        min_communs=1,
        min_degre=0,
    )

    paires = [
        (c.fichier_a, c.fichier_b)
        for c in resultat
    ]

    assert paires == [
        ("a.php", "b.php"),
        ("a.php", "c.php"),
        ("b.php", "c.php"),
    ]


def test_couplage_limite_resultats():
    commits = [
        ["a.php", "b.php", "c.php"],
        ["a.php", "b.php", "c.php"],
    ]

    resultat = calculer_couplages(
        commits,
        {"a.php", "b.php", "c.php"},
        min_communs=1,
        min_degre=0,
        limite=2,
    )

    assert len(resultat) == 2


def test_croiser_dependance_statique_directe():
    couplages = [
        Couplage("a.php", "b.php", 8, 0.8, False)
    ]
    dependances = {"a.php": ["b.php"], "b.php": []}

    resultat = croiser(couplages, dependances)

    assert resultat[0].lien_statique is True


def test_croiser_dependance_statique_inverse():
    couplages = [
        Couplage("a.php", "b.php", 8, 0.8, False)
    ]
    dependances = {"a.php": [], "b.php": ["a.php"]}

    resultat = croiser(couplages, dependances)

    assert resultat[0].lien_statique is True


def test_croiser_couplage_cache():
    couplages = [
        Couplage("a.php", "b.php", 8, 0.8, False)
    ]
    dependances = {"a.php": [], "b.php": []}

    resultat = croiser(couplages, dependances)

    assert resultat[0].lien_statique is False


def test_degre_prend_en_compte_les_commits_solos():
    commits = [
        ["A.php", "B.php"],
        ["A.php", "B.php"],
        ["A.php", "C.php"],
        ["A.php"],
    ]

    resultat = calculer_couplages(
        commits,
        {"A.php", "B.php", "C.php"},
        min_communs=2,
        min_degre=0,
    )

    couplage_ab = next(
        c for c in resultat
        if c.fichier_a == "A.php" and c.fichier_b == "B.php"
    )

    assert couplage_ab.commits_communs == 2
    assert couplage_ab.degre == pytest.approx(2 / 3)