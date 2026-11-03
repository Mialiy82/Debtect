import json
import subprocess

from debtect.cli import main


def creer_depot_git(chemin):
    subprocess.run(
        ["git", "init"],
        cwd=chemin,
        capture_output=True,
        check=True,
    )


def creer_commit(chemin):
    subprocess.run(
        ["git", "add", "."],
        cwd=chemin,
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
        cwd=chemin,
        capture_output=True,
        check=True,
    )


def test_cli_depot_valide_avec_erreur_parsing(tmp_path, capsys):
    depot = tmp_path / "depot"
    depot.mkdir()

    creer_depot_git(depot)

    (depot / "ok.php").write_text(
        """<?php
function demo($x) {
    if ($x > 0) {
        return true;
    }
    return false;
}
""",
        encoding="utf-8",
    )

    (depot / "casse.php").write_text(
        """<?php
function demo( {
""",
        encoding="utf-8",
    )

    creer_commit(depot)

    sortie = tmp_path / "rapport.json"

    code = main([str(depot), "-o", str(sortie)])

    assert code == 0
    assert sortie.exists()

    rapport = json.loads(sortie.read_text(encoding="utf-8"))

    assert len(rapport["fichiers"]) == 1

    fichier = rapport["fichiers"][0]

    assert fichier["chemin"] == "ok.php"
    assert fichier["complexite_totale"] == 2
    assert fichier["churn"] == 1
    assert fichier["score_hotspot"] == 2.0

    assert rapport["fichiers_echec"] == ["casse.php"]


def test_cli_dossier_non_git(tmp_path, capsys):
    code = main([str(tmp_path)])

    capture = capsys.readouterr()

    assert code == 1
    assert "Erreur Git" in capture.err
