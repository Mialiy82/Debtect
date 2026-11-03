"""Tests unitaires — à remplir en Vérification/Validation. Jamais de disque/git ici."""

from debtect.parser import parser
from debtect.complexity import calculer


def analyser_php(tmp_path, contenu):
    fichier = tmp_path / "test.php"
    fichier.write_text(contenu, encoding="utf-8")

    ast = parser(fichier)

    return calculer(ast)


def test_complexite_if_else(tmp_path):
    contenu = """<?php
function demo($x) {
    if ($x > 0) {
        return "positif";
    } else {
        return "negatif";
    }
}
"""

    fonctions = analyser_php(tmp_path, contenu)

    assert len(fonctions) == 1
    assert fonctions[0].nom == "demo"
    assert fonctions[0].complexite == 2


def test_complexite_if_elseif_else(tmp_path):
    contenu = """<?php
function demo($x) {
    if ($x > 0) {
        return "positif";
    } elseif ($x < 0) {
        return "negatif";
    } else {
        return "zero";
    }
}
"""

    fonctions = analyser_php(tmp_path, contenu)

    assert len(fonctions) == 1
    assert fonctions[0].complexite == 3


def test_complexite_boucles_et_conditions(tmp_path):
    contenu = """<?php
function demo($x) {
    if ($x > 0) {
        for ($i = 0; $i < $x; $i++) {
            if ($i % 2 == 0) {
                echo $i;
            }
        }
    } else {
        while ($x < 0) {
            $x++;
        }
    }
}
"""

    fonctions = analyser_php(tmp_path, contenu)

    assert len(fonctions) == 1
    assert fonctions[0].complexite == 5
