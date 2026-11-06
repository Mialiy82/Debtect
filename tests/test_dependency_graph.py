from pathlib import Path
import pytest

from debtect.dependency_graph import extraire, _construire_index, _resoudre_reference, resoudre, inverser, impact, ErreurImpact
from debtect.models import InfoDependances
from debtect.parser import parser


def test_extraire_namespace_et_declarations(tmp_path):
    fichier = tmp_path / "Document.php"
    fichier.write_text(
        """
        <?php
        namespace App\\Models;

        class Document {}
        interface Printable {}
        trait Loggable {}
        enum Status {}
        """,
        encoding="utf-8",
    )

    ast = parser(fichier)
    resultat = extraire(ast)

    assert resultat.espace_de_noms == "App\\Models"
    assert resultat.declarations == [
        "App\\Models\\Document",
        "App\\Models\\Printable",
        "App\\Models\\Loggable",
        "App\\Models\\Status",
    ]

def test_import_simple(tmp_path):
    fichier = tmp_path / "Test.php"
    fichier.write_text(
        "<?php namespace App; use App\\Models\\Document;",
        encoding="utf-8",
    )

    resultat = extraire(parser(fichier))

    assert resultat.imports == {
        "Document": "App\\Models\\Document"
    }


def test_import_groupe(tmp_path):
    fichier = tmp_path / "Test.php"
    fichier.write_text(
        "<?php namespace App; use App\\Models\\{Document, Contact};",
        encoding="utf-8",
    )

    resultat = extraire(parser(fichier))

    assert resultat.imports == {
        "Document": "App\\Models\\Document",
        "Contact": "App\\Models\\Contact",
    }


def test_import_avec_alias(tmp_path):
    fichier = tmp_path / "Test.php"
    fichier.write_text(
        "<?php namespace App; use App\\Models\\Contact as Client;",
        encoding="utf-8",
    )

    resultat = extraire(parser(fichier))

    assert resultat.imports == {
        "Client": "App\\Models\\Contact"
    }

def test_import_function_ignore(tmp_path):
    fichier = tmp_path / "Test.php"
    fichier.write_text(
        "<?php namespace App; use function App\\Helpers\\format;",
        encoding="utf-8",
    )

    resultat = extraire(parser(fichier))

    assert resultat.imports == {}


def test_import_const_ignore(tmp_path):
    fichier = tmp_path / "Test.php"
    fichier.write_text(
        "<?php namespace App; use const App\\Config\\VERSION;",
        encoding="utf-8",
    )

    resultat = extraire(parser(fichier))

    assert resultat.imports == {}


def test_extraire_extends(tmp_path):
    fichier = tmp_path / "Test.php"
    fichier.write_text(
        "<?php namespace App; class Document extends Model {}",
        encoding="utf-8",
    )

    resultat = extraire(parser(fichier))

    assert resultat.references == ["Model"]


def test_extraire_implements(tmp_path):
    fichier = tmp_path / "Test.php"
    fichier.write_text(
        "<?php namespace App; class Document implements Printable, Jsonable {}",
        encoding="utf-8",
    )

    resultat = extraire(parser(fichier))

    assert resultat.references == ["Printable", "Jsonable"]


def test_extraire_traits(tmp_path):
    fichier = tmp_path / "Test.php"
    fichier.write_text(
        "<?php namespace App; class Document { use Loggable, Timestampable; }",
        encoding="utf-8",
    )

    resultat = extraire(parser(fichier))

    assert resultat.references == ["Loggable", "Timestampable"]

def test_extraire_reference_absolue(tmp_path):
    fichier = tmp_path / "Test.php"
    fichier.write_text(
        "<?php namespace App; class Job extends \\Illuminate\\Foundation\\Bus\\Dispatchable {}",
        encoding="utf-8",
    )

    resultat = extraire(parser(fichier))

    assert resultat.references == [
        "\\Illuminate\\Foundation\\Bus\\Dispatchable"
    ]


def test_extraire_reference_qualifiee(tmp_path):
    fichier = tmp_path / "Test.php"
    fichier.write_text(
        "<?php namespace App; class Job { use Helpers\\Formatter; }",
        encoding="utf-8",
    )

    resultat = extraire(parser(fichier))

    assert resultat.references == ["Helpers\\Formatter"]


def test_construire_index():
    infos = {
        "Models/Document.php": InfoDependances(
            espace_de_noms="App\\Models",
            declarations=["App\\Models\\Document"],
            imports={},
            references=[],
        ),
        "Abstracts/Model.php": InfoDependances(
            espace_de_noms="App\\Abstracts",
            declarations=["App\\Abstracts\\Model"],
            imports={},
            references=[],
        ),
    }

    resultat = _construire_index(infos)

    assert resultat == {
    "app\\models\\document": ["Models/Document.php"],
    "app\\abstracts\\model": ["Abstracts/Model.php"],
}

def test_resoudre_reference_absolue():
    info = InfoDependances("App", [], {}, [])

    resultat = _resoudre_reference(
        "\\Illuminate\\Database\\Model",
        info,
    )

    assert resultat == "Illuminate\\Database\\Model"


def test_resoudre_reference_import():
    info = InfoDependances(
        "App\\Models",
        [],
        {"Model": "App\\Abstracts\\Model"},
        [],
    )

    resultat = _resoudre_reference("Model", info)

    assert resultat == "App\\Abstracts\\Model"


def test_resoudre_reference_namespace():
    info = InfoDependances("App\\Models", [], {}, [])

    resultat = _resoudre_reference("Model", info)

    assert resultat == "App\\Models\\Model"


def test_resoudre_reference_qualifiee_avec_import():
    info = InfoDependances(
        "App",
        [],
        {"Helpers": "App\\Support\\Helpers"},
        [],
    )

    resultat = _resoudre_reference("Helpers\\Formatter", info)

    assert resultat == "App\\Support\\Helpers\\Formatter"

def test_resoudre_dependance_avec_import():
    infos = {
        "Models/Document.php": InfoDependances(
            "App\\Models",
            ["App\\Models\\Document"],
            {"Model": "App\\Abstracts\\Model"},
            ["Model"],
        ),
        "Abstracts/Model.php": InfoDependances(
            "App\\Abstracts",
            ["App\\Abstracts\\Model"],
            {},
            [],
        ),
    }

    resultat = resoudre(infos)

    assert resultat == {
        "Models/Document.php": ["Abstracts/Model.php"],
        "Abstracts/Model.php": [],
    }


def test_resoudre_ignore_dependance_inexistante():
    infos = {
        "Models/Document.php": InfoDependances(
            "App\\Models",
            ["App\\Models\\Document"],
            {},
            ["External\\Unknown"],
        ),
    }

    resultat = resoudre(infos)

    assert resultat == {
        "Models/Document.php": [],
    }


def test_resoudre_ignore_dependance_vers_soi_meme():
    infos = {
        "Models/Document.php": InfoDependances(
            "App\\Models",
            ["App\\Models\\Document"],
            {},
            ["Document"],
        ),
    }

    resultat = resoudre(infos)

    assert resultat == {
        "Models/Document.php": [],
    }

def test_resoudre_declarations_dupliquees():
    infos = {
        "z.php": InfoDependances(
            espace_de_noms="App",
            declarations=["App\\A"],
            imports={},
            references=[],
        ),
        "a.php": InfoDependances(
            espace_de_noms="App",
            declarations=["App\\A"],
            imports={},
            references=[],
        ),
        "consumer.php": InfoDependances(
            espace_de_noms="App",
            declarations=[],
            imports={"A": "App\\A"},
            references=[],
        ),
    }

    graphe = resoudre(infos)

    assert graphe["consumer.php"] == ["a.php", "z.php"]

def test_resoudre_dependance_import_sans_reference():
    infos = {
        "tax.php": InfoDependances(
            espace_de_noms="App\\Models\\Setting",
            declarations=["App\\Models\\Setting\\Tax"],
            imports={},
            references=[],
        ),
        "document.php": InfoDependances(
            espace_de_noms="App\\Models\\Document",
            declarations=["App\\Models\\Document\\Document"],
            imports={"Tax": "App\\Models\\Setting\\Tax"},
            references=[],
        ),
    }

    graphe = resoudre(infos)

    assert graphe["document.php"] == ["tax.php"]

def test_resoudre_dependances_triees():
    infos = {
        "z.php": InfoDependances(
            espace_de_noms="App",
            declarations=["App\\Z"],
            imports={},
            references=[],
        ),
        "a.php": InfoDependances(
            espace_de_noms="App",
            declarations=["App\\A"],
            imports={},
            references=[],
        ),
        "b.php": InfoDependances(
            espace_de_noms="App",
            declarations=["App\\B"],
            imports={},
            references=[],
        ),
        "consumer.php": InfoDependances(
            espace_de_noms="App",
            declarations=[],
            imports={},
            references=["Z", "B", "A"],
        ),
    }

    graphe = resoudre(infos)

    assert graphe["consumer.php"] == ["a.php", "b.php", "z.php"]

def test_extraire_traits_avec_conflit(tmp_path):
    source = """<?php
    class X {
        use A, B {
            A::hello insteadof B;
        }
    }
    """

    fichier = tmp_path / "test.php"
    fichier.write_text(source, encoding="utf-8")

    ast = parser(str(fichier))
    resultat = extraire(ast)

    assert resultat.references == ["A", "B"]

def test_inverser():
    dependances = {
        "A.php": ["B.php", "C.php"],
        "B.php": ["C.php"],
        "C.php": [],
        "D.php": [],
    }

    resultat = inverser(dependances)

    assert resultat == {
        "A.php": [],
        "B.php": ["A.php"],
        "C.php": ["A.php", "B.php"],
        "D.php": [],
    }

def test_impact_chaine():
    dependances = {
        "A.php": [],
        "B.php": ["A.php"],
        "C.php": ["B.php"],
    }

    resultat = impact(dependances, "A.php")

    assert resultat == {
        "B.php": 1,
        "C.php": 2,
    }


def test_impact_losange_distance_plus_courte():
    dependances = {
        "A.php": [],
        "B.php": ["A.php"],
        "C.php": ["A.php"],
        "D.php": ["B.php", "C.php"],
    }

    resultat = impact(dependances, "A.php")

    assert resultat == {
        "B.php": 1,
        "C.php": 1,
        "D.php": 2,
    }


def test_impact_cycle():
    dependances = {
        "A.php": ["B.php"],
        "B.php": ["A.php"],
    }

    resultat = impact(dependances, "A.php")

    assert resultat == {
        "B.php": 1,
    }


def test_impact_profondeur_limitee():
    dependances = {
        "A.php": [],
        "B.php": ["A.php"],
        "C.php": ["B.php"],
    }

    resultat = impact(dependances, "A.php", profondeur=1)

    assert resultat == {
        "B.php": 1,
    }


def test_impact_sans_dependant():
    dependances = {
        "A.php": [],
        "B.php": ["A.php"],
    }

    resultat = impact(dependances, "B.php")

    assert resultat == {}


def test_impact_cible_inconnue():
    dependances = {
        "A.php": [],
        "B.php": ["A.php"],
    }

    with pytest.raises(ErreurImpact):
        impact(dependances, "inconnu.php")