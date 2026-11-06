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

    code = main(["analyser", str(depot), "-o", str(sortie)])

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
    code = main(["analyser", str(tmp_path)])

    capture = capsys.readouterr()

    assert code == 1
    assert "Erreur Git" in capture.err


def test_cli_resout_dependance_entre_fichiers(tmp_path):
    depot = tmp_path / "depot"
    depot.mkdir()

    creer_depot_git(depot)

    app = depot / "app"
    app.mkdir()

    (app / "A.php").write_text(
        """<?php
namespace App;

class A {}
""",
        encoding="utf-8",
    )

    (app / "B.php").write_text(
        """<?php
namespace App;

class B extends A {}
""",
        encoding="utf-8",
    )

    creer_commit(depot)

    sortie = tmp_path / "rapport.json"

    code = main(["analyser", str(depot), "-o", str(sortie)])

    assert code == 0
    assert sortie.exists()

    rapport = json.loads(sortie.read_text(encoding="utf-8"))

    fichiers = {fichier["chemin"]: fichier for fichier in rapport["fichiers"]}

    assert fichiers["app/A.php"]["dependances"] == []
    assert fichiers["app/B.php"]["dependances"] == ["app/A.php"]


def test_cli_declarations_dupliquees(tmp_path):
    depot = tmp_path / "depot"
    depot.mkdir()

    creer_depot_git(depot)

    app = depot / "app"
    app.mkdir()

    (app / "A1.php").write_text(
        """<?php
namespace App;

class A {}
""",
        encoding="utf-8",
    )

    (app / "A2.php").write_text(
        """<?php
namespace App;

class A {}
""",
        encoding="utf-8",
    )

    (app / "B.php").write_text(
        """<?php
namespace App;

class B extends A {}
""",
        encoding="utf-8",
    )

    creer_commit(depot)

    sortie = tmp_path / "rapport.json"

    code = main(["analyser", str(depot), "-o", str(sortie)])

    assert code == 0
    assert sortie.exists()

    rapport = json.loads(sortie.read_text(encoding="utf-8"))

    fichiers = {fichier["chemin"]: fichier for fichier in rapport["fichiers"]}

    assert fichiers["app/B.php"]["dependances"] == [
        "app/A1.php",
        "app/A2.php",
    ]


def test_cli_impact_cas_nominal(tmp_path, capsys):
    rapport = {
        "fichiers": [
            {
                "chemin": "app/A.php",
                "dependances": [],
                "score_hotspot": 10.0,
            },
            {
                "chemin": "app/B.php",
                "dependances": ["app/A.php"],
                "score_hotspot": 5.0,
            },
        ]
    }

    fichier_json = tmp_path / "rapport.json"
    fichier_json.write_text(
        json.dumps(rapport),
        encoding="utf-8",
    )

    code = main(
        [
            "impact",
            str(fichier_json),
            "app/A.php",
        ]
    )

    capture = capsys.readouterr()

    assert code == 0
    assert "app/B.php" in capture.out
    assert "Niveau 1" in capture.out


def test_cli_impact_cible_inconnue(tmp_path, capsys):
    rapport = {
        "fichiers": [
            {
                "chemin": "app/A.php",
                "dependances": [],
                "score_hotspot": 0.0,
            }
        ]
    }

    fichier_json = tmp_path / "rapport.json"
    fichier_json.write_text(
        json.dumps(rapport),
        encoding="utf-8",
    )

    code = main(
        [
            "impact",
            str(fichier_json),
            "app/Inconnue.php",
        ]
    )

    capture = capsys.readouterr()

    assert code == 1
    assert capture.err


def test_cli_impact_json_inexistant(tmp_path):
    fichier_json = tmp_path / "inexistant.json"

    code = main(
        [
            "impact",
            str(fichier_json),
            "app/A.php",
        ]
    )

    assert code == 1
