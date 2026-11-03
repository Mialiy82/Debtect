import subprocess

import pytest

from debtect.git_miner import _compter, churn, ErreurGit


def test_compter_churn():
    texte = """app/Models/User.php
app/Models/Bill.php
app/Models/User.php

app/Models/Invoice.php
app/Models/Bill.php
app/Models/User.php
"""

    resultat = _compter(texte)

    assert resultat == {
        "app/Models/User.php": 3,
        "app/Models/Bill.php": 2,
        "app/Models/Invoice.php": 1,
    }


def test_compter_texte_vide():
    assert _compter("") == {}


def test_churn_chemin_inexistant(tmp_path):
    chemin = tmp_path / "inexistant"

    with pytest.raises(ErreurGit):
        churn(str(chemin))


def test_churn_dossier_non_git(tmp_path):
    with pytest.raises(ErreurGit, match="Échec de Git"):
        churn(str(tmp_path))


def test_churn_sous_dossier_du_depot(tmp_path):
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )

    sous_dossier = tmp_path / "app"
    sous_dossier.mkdir()

    with pytest.raises(ErreurGit, match="n'est pas la racine"):
        churn(str(sous_dossier))


def test_churn_depot_avec_commit(tmp_path):
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )

    fichier = tmp_path / "User.php"
    fichier.write_text(
        "<?php\nfunction user() { return true; }\n",
        encoding="utf-8",
    )

    subprocess.run(
        ["git", "add", "."],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )

    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-m",
            "Premier commit",
        ],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )

    resultat = churn(str(tmp_path))

    assert resultat == {"User.php": 1}
